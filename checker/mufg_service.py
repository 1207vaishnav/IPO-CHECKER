import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re


MUFG_URL = "https://in.mpms.mufg.com/Initial_Offer/public-issues.html"


def check_mufg_multiple(pans, ipo_name):
    """
    Check multiple PANs using ONE Playwright browser.

    This is faster than launching a new Chromium browser
    for every PAN.
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
        # START BROWSER ONLY ONCE
        # =========================================
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/ms-playwright"

        browser = p.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ],
)

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/150.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        # Short timeout
        page.set_default_timeout(10000)

        try:

            # =========================================
            # OPEN MUFG ONLY ONCE
            # =========================================

            print("Opening MUFG website...")

            page.goto(
                MUFG_URL,
                wait_until="domcontentloaded",
                timeout=20000
            )

            print("MUFG page opened")


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
                    ipo_name
                )

                results[pan_number] = result


        except Exception as e:

            print(
                "MUFG bulk error:",
                e
            )

            for pan_number in pans:

                if pan_number not in results:

                    results[pan_number] = {
                        "status": "MUFG Request Failed",
                        "shares": 0,
                        "name": ""
                    }

        finally:

            browser.close()

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

        page.goto(
            MUFG_URL,
            wait_until="domcontentloaded",
            timeout=15000
        )


        # =========================================
        # 2. COMPANY DROPDOWN
        # =========================================

        company_dropdown = page.locator(
            "#ddlCompany"
        )

        company_dropdown.wait_for(
            state="visible",
            timeout=5000
        )


        # =========================================
        # 3. FIND IPO
        # =========================================

        ipo_search_name = ipo_name.replace(
            " IPO",
            ""
        ).strip()

        option = company_dropdown.locator(
            "option",
            has_text=ipo_search_name
        )


        # Fallback

        if option.count() == 0:

            option = company_dropdown.locator(
                "option",
                has_text="Lalithaa Jewellery"
            )


        if option.count() == 0:

            return {
                "status": "IPO Not Found",
                "shares": 0,
                "name": ""
            }


        ipo_value = option.first.get_attribute(
            "value"
        )

        print(
            "IPO value:",
            ipo_value
        )


        # =========================================
        # 4. SELECT IPO
        # =========================================

        company_dropdown.select_option(
            value=ipo_value
        )


        # =========================================
        # 5. SELECT PAN
        # =========================================

        pan_radio = page.locator(
            'input[type="radio"][value="PAN"]'
        )

        if pan_radio.count() > 0:

            pan_radio.check()


        # =========================================
        # 6. ENTER PAN
        # =========================================

        pan_input = page.locator(
            "#txtStat"
        )

        pan_input.wait_for(
            state="visible",
            timeout=5000
        )

        pan_input.fill(
            pan_number.strip().upper()
        )


        # =========================================
        # 7. CAPTCHA
        # =========================================

        captcha = page.locator(
            "#txtCaptch"
        )

        if captcha.count() > 0:

            try:

                if captcha.is_visible():

                    print(
                        "CAPTCHA REQUIRED"
                    )

                    return {
                        "status": "CAPTCHA Required",
                        "shares": 0,
                        "name": ""
                    }

            except Exception:

                pass


        # =========================================
        # 8. SUBMIT
        # =========================================

        submit_button = page.locator(
            "#btnsearc"
        )

        submit_button.wait_for(
            state="visible",
            timeout=5000
        )

        submit_button.click()


        # =========================================
        # 9. WAIT FOR RESULT
        # =========================================

        allotted_text = page.get_by_text(
            "Securities Allotted",
            exact=False
        )

        try:

            allotted_text.wait_for(
                state="visible",
                timeout=10000
            )

        except PlaywrightTimeoutError:

            return {
                "status": "Result Not Found",
                "shares": 0,
                "name": ""
            }


        # =========================================
        # 10. GET APPLICANT NAME
        # =========================================

        name = ""

        try:

            applicant_text = page.get_by_text(
                "Sole / 1st Applicant",
                exact=False
            )

            if applicant_text.count() > 0:

                applicant_row = applicant_text.first.locator(
                    "xpath=.."
                )

                applicant_row_text = (
                    applicant_row.inner_text().strip()
                )

                print(
                    "Applicant row:",
                    applicant_row_text
                )


                # Remove label

                name = re.sub(
                    r"Sole\s*/\s*1st\s*Applicant",
                    "",
                    applicant_row_text,
                    flags=re.IGNORECASE
                ).strip()


                name = name.strip(
                    " :.-"
                )


        except Exception as e:

            print(
                "Could not read applicant name:",
                e
            )


        # =========================================
        # 11. GET ALLOTTED SHARES
        # =========================================

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
                row_text
            )


            numbers = re.findall(
                r"\b\d+\b",
                row_text
            )


            if numbers:

                shares = int(
                    numbers[-1]
                )


        except Exception as e:

            print(
                "Could not read allotted shares:",
                e
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
        print(
            "Name:",
            name
        )

        print(
            "Status:",
            status
        )

        print(
            "Shares:",
            shares
        )


        return {

            "name": name,

            "status": status,

            "shares": shares

        }


    except PlaywrightTimeoutError as e:

        print(
            "MUFG timeout:",
            e
        )

        return {

            "status": "MUFG Timeout",

            "shares": 0,

            "name": ""

        }


    except Exception as e:

        print(
            "MUFG error:",
            e
        )

        return {

            "status": "MUFG Request Failed",

            "shares": 0,

            "name": ""

        }