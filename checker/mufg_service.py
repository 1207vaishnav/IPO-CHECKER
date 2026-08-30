import os
import re

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


MUFG_URL = "https://in.mpms.mufg.com/Initial_Offer/public-issues.html"


def check_mufg_multiple(pans, ipo_name):
    """
    Check multiple PANs using ONE Playwright browser.
    """

    results = {}

    print()
    print("========================================")
    print("STARTING MUFG BULK CHECK")
    print("IPO:", ipo_name)
    print("PAN COUNT:", len(pans))
    print("========================================")

    with sync_playwright() as p:

        # =========================================
        # PLAYWRIGHT BROWSER PATH
        # =========================================

        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"

        print("Launching Chromium...")

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        print("Chromium launched successfully")

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/150.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        # =========================================
        # DEFAULT TIMEOUT
        # =========================================

        page.set_default_timeout(30000)

        try:

            # =========================================
            # OPEN MUFG WEBSITE
            # =========================================

            print("Opening MUFG website...")

            page.goto(
                MUFG_URL,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            print("MUFG page opened")
            print("Current URL:", page.url)

            # =========================================
            # CHECK EVERY PAN
            # =========================================

            for pan_number in pans:

                print()
                print("----------------------------------------")
                print("Checking PAN:", pan_number)
                print("----------------------------------------")

                result = check_single_pan(
                    page,
                    pan_number,
                    ipo_name,
                )

                results[pan_number] = result

        except Exception as e:

            print("MUFG bulk error:", repr(e))

            for pan_number in pans:

                if pan_number not in results:

                    results[pan_number] = {
                        "status": "MUFG Request Failed",
                        "shares": 0,
                        "name": "",
                    }

        finally:

            print("Closing browser...")

            try:
                browser.close()
            except Exception as e:
                print("Browser close error:", repr(e))

    print()
    print("========================================")
    print("MUFG BULK CHECK COMPLETED")
    print("========================================")

    return results


def check_single_pan(page, pan_number, ipo_name):

    try:

        # =========================================
        # 1. RELOAD MUFG PAGE
        # =========================================

        print("Step 1: Opening MUFG page...")

        page.goto(
            MUFG_URL,
            wait_until="domcontentloaded",
            timeout=30000,
        )

        print("Step 1 complete")

        # =========================================
        # 2. COMPANY DROPDOWN
        # =========================================

        print("Step 2: Looking for company dropdown...")

        company_dropdown = page.locator(
            "#ddlCompany"
        )

        company_dropdown.wait_for(
            state="visible",
            timeout=30000,
        )

        print("Step 2 complete: Company dropdown found")

        # =========================================
        # 3. FIND IPO
        # =========================================

        print("Step 3: Searching for IPO:", ipo_name)

        ipo_search_name = ipo_name.replace(
            " IPO",
            "",
        ).strip()

        option = company_dropdown.locator(
            "option",
            has_text=ipo_search_name,
        )

        # =========================================
        # FALLBACK
        # =========================================

        if option.count() == 0:

            print(
                "IPO not found using name:",
                ipo_search_name,
            )

            option = company_dropdown.locator(
                "option",
                has_text="Lalithaa Jewellery",
            )

        if option.count() == 0:

            print("IPO not found in dropdown")

            return {
                "status": "IPO Not Found",
                "shares": 0,
                "name": "",
            }

        ipo_value = option.first.get_attribute(
            "value"
        )

        print("IPO value:", ipo_value)

        # =========================================
        # 4. SELECT IPO
        # =========================================

        print("Step 4: Selecting IPO...")

        company_dropdown.select_option(
            value=ipo_value
        )

        print("Step 4 complete")

        # =========================================
        # 5. SELECT PAN
        # =========================================

        print("Step 5: Selecting PAN option...")

        pan_radio = page.locator(
            'input[type="radio"][value="PAN"]'
        )

        if pan_radio.count() > 0:

            pan_radio.check()

            print("PAN option selected")

        else:

            print("PAN radio button not found")

        # =========================================
        # 6. ENTER PAN
        # =========================================

        print("Step 6: Looking for PAN input...")

        pan_input = page.locator(
            "#txtStat"
        )

        pan_input.wait_for(
            state="visible",
            timeout=30000,
        )

        print("PAN input found")

        pan_input.fill(
            pan_number.strip().upper()
        )

        print("PAN entered")

        # =========================================
        # 7. CAPTCHA
        # =========================================

        print("Step 7: Checking CAPTCHA...")

        captcha = page.locator(
            "#txtCaptch"
        )

        if captcha.count() > 0:

            try:

                if captcha.is_visible():

                    print("CAPTCHA REQUIRED")

                    return {
                        "status": "CAPTCHA Required",
                        "shares": 0,
                        "name": "",
                    }

            except Exception:
                pass

        print("No visible CAPTCHA detected")

        # =========================================
        # 8. SUBMIT
        # =========================================

        print("Step 8: Looking for submit button...")

        submit_button = page.locator(
            "#btnsearc"
        )

        submit_button.wait_for(
            state="visible",
            timeout=30000,
        )

        print("Submit button found")

        submit_button.click()

        print("Submit button clicked")

        # =========================================
        # 9. WAIT FOR RESULT
        # =========================================

        print("Step 9: Waiting for MUFG result...")

        allotted_text = page.get_by_text(
            "Securities Allotted",
            exact=False,
        )

        try:

            allotted_text.wait_for(
                state="visible",
                timeout=30000,
            )

            print("MUFG result found")

        except PlaywrightTimeoutError:

            print(
                "Result text 'Securities Allotted' "
                "was not found within 30 seconds"
            )

            print(
                "Current URL:",
                page.url,
            )

            return {
                "status": "Result Not Found",
                "shares": 0,
                "name": "",
            }

        # =========================================
        # 10. GET APPLICANT NAME
        # =========================================

        print("Step 10: Reading applicant name...")

        name = ""

        try:

            applicant_text = page.get_by_text(
                "Sole / 1st Applicant",
                exact=False,
            )

            if applicant_text.count() > 0:

                applicant_row = (
                    applicant_text.first.locator(
                        "xpath=.."
                    )
                )

                applicant_row_text = (
                    applicant_row.inner_text().strip()
                )

                print(
                    "Applicant row:",
                    applicant_row_text,
                )

                # Remove label

                name = re.sub(
                    r"Sole\s*/\s*1st\s*Applicant",
                    "",
                    applicant_row_text,
                    flags=re.IGNORECASE,
                ).strip()

                name = name.strip(
                    " :.-"
                )

        except Exception as e:

            print(
                "Could not read applicant name:",
                repr(e),
            )

        # =========================================
        # 11. GET ALLOTTED SHARES
        # =========================================

        print("Step 11: Reading allotted shares...")

        shares = 0

        try:

            row = allotted_text.first.locator(
                "xpath=.."
            )

            row_text = (
                row.inner_text().strip()
            )

            print(
                "Allotted row:",
                row_text,
            )

            numbers = re.findall(
                r"\b\d+\b",
                row_text,
            )

            if numbers:

                shares = int(
                    numbers[-1]
                )

        except Exception as e:

            print(
                "Could not read allotted shares:",
                repr(e),
            )

            shares = 0

        # =========================================
        # 12. STATUS
        # =========================================

        if shares > 0:

            status = "Allotted"

        else:

            status = "Not Allotted"

        # =========================================
        # 13. RESULT
        # =========================================

        print()
        print("Name:", name)
        print("Status:", status)
        print("Shares:", shares)

        return {
            "name": name,
            "status": status,
            "shares": shares,
        }

    except PlaywrightTimeoutError as e:

        print(
            "MUFG timeout:",
            repr(e),
        )

        return {
            "status": "MUFG Timeout",
            "shares": 0,
            "name": "",
        }

    except Exception as e:

        print(
            "MUFG error:",
            repr(e),
        )

        return {
            "status": "MUFG Request Failed",
            "shares": 0,
            "name": "",
        }