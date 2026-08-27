from django.shortcuts import render
from .models import PAN, IPO, Allotment
from .services import check_ipo_allotment
from .mufg_service import check_mufg_multiple
import re


def home(request):

    message = ""
    selected_pans = []
    selected_ipo = ""
    results = []

    if request.method == "POST":

        # =========================================
        # 1. ADD PAN
        # =========================================

        pan_number = request.POST.get(
            "pan_number",
            ""
        ).strip().upper()

        if pan_number:

            if re.fullmatch(
                r"[A-Z]{5}[0-9]{4}[A-Z]",
                pan_number
            ):

                PAN.objects.get_or_create(
                    pan_number=pan_number
                )

                message = "PAN saved successfully."

            else:

                message = (
                    "Invalid PAN. "
                    "Please enter a valid 10-character PAN."
                )


        # =========================================
        # 2. EDIT PAN
        # =========================================

        edit_pan_id = request.POST.get(
            "edit_pan_id"
        )

        edit_pan_number = request.POST.get(
            "edit_pan_number",
            ""
        ).strip().upper()


        if edit_pan_id:

            if not re.fullmatch(
                r"[A-Z]{5}[0-9]{4}[A-Z]",
                edit_pan_number
            ):

                message = (
                    "Invalid PAN. "
                    "Please enter a valid 10-character PAN."
                )

            else:

                try:

                    pan = PAN.objects.get(
                        id=edit_pan_id
                    )

                    existing_pan = PAN.objects.filter(
                        pan_number=edit_pan_number
                    ).exclude(
                        id=edit_pan_id
                    ).first()


                    if existing_pan:

                        message = (
                            "This PAN is already saved."
                        )

                    else:

                        pan.pan_number = edit_pan_number

                        pan.save(
                            update_fields=[
                                "pan_number"
                            ]
                        )

                        message = (
                            "PAN updated successfully."
                        )


                except PAN.DoesNotExist:

                    message = "PAN not found."


        # =========================================
        # 3. DELETE PAN
        # =========================================

        delete_pan = request.POST.get(
            "delete_pan"
        )

        if delete_pan:

            PAN.objects.filter(
                id=delete_pan
            ).delete()

            message = (
                "PAN deleted successfully."
            )


        # =========================================
        # 4. CHECK ALLOTMENT
        # =========================================

        if (
            "check_allotment" in request.POST
            or
            "check_all_pans" in request.POST
        ):

            # -----------------------------------------
            # GET SELECTED PAN IDS
            # -----------------------------------------

            selected_ids = request.POST.getlist(
                "selected_pans"
            )


            # -----------------------------------------
            # GET SELECTED PANS
            # -----------------------------------------

            selected_pans = PAN.objects.filter(
                id__in=selected_ids
            )


            # -----------------------------------------
            # CHECK ALL PANS
            # -----------------------------------------

            if "check_all_pans" in request.POST:

                selected_pans = PAN.objects.all()


            # -----------------------------------------
            # GET IPO
            # -----------------------------------------

            selected_ipo = request.POST.get(
                "ipo",
                ""
            )

            selected_ipo_object = None

            if selected_ipo:

                selected_ipo_object = IPO.objects.filter(
                    id=selected_ipo
                ).first()


            # -----------------------------------------
            # VALIDATE PANS
            # -----------------------------------------

            if not selected_pans:

                message = (
                    "Please select at least one PAN."
                )


            # -----------------------------------------
            # VALIDATE IPO
            # -----------------------------------------

            elif not selected_ipo_object:

                message = (
                    "Please select an IPO."
                )


            # -----------------------------------------
            # START CHECK
            # -----------------------------------------

            else:

                message = (
                    "Checking allotment..."
                )


                # =====================================
                # MUFG BULK CHECK
                # =====================================

                if selected_ipo_object.registrar == "MUFG Intime":

                    pan_numbers = [
                        pan.pan_number
                        for pan in selected_pans
                    ]


                    print()
                    print(
                        "======================================"
                    )

                    print(
                        "STARTING FAST MUFG BULK CHECK"
                    )

                    print(
                        "PAN COUNT:",
                        len(pan_numbers)
                    )

                    print(
                        "======================================"
                    )


                    mufg_results = check_mufg_multiple(

                        pan_numbers,

                        selected_ipo_object.name

                    )


                    # =================================
                    # PROCESS MUFG RESULTS
                    # =================================

                    for pan in selected_pans:

                        response = mufg_results.get(

                            pan.pan_number,

                            {

                                "name": "",

                                "status": "MUFG Request Failed",

                                "shares": 0

                            }

                        )


                        name = response.get(
                            "name",
                            ""
                        ).strip()


                        status = response.get(
                            "status",
                            "Unknown"
                        )


                        shares = response.get(
                            "shares",
                            0
                        )


                        # -----------------------------
                        # SAVE NAME
                        # -----------------------------

                        if name:

                            pan.name = name

                            pan.save(
                                update_fields=[
                                    "name"
                                ]
                            )


                        # -----------------------------
                        # DISPLAY NAME
                        # -----------------------------

                        display_name = (

                            name

                            or

                            pan.name

                            or

                            "Name Not Available"

                        )


                        # -----------------------------
                        # SAVE RESULT
                        # -----------------------------

                        Allotment.objects.update_or_create(

                            pan=pan,

                            ipo=selected_ipo_object,

                            defaults={

                                "status": status,

                                "shares": shares

                            }

                        )


                        # -----------------------------
                        # ADD RESULT
                        # -----------------------------

                        results.append({

                            "name": display_name,

                            "status": status,

                            "shares": shares

                        })


                # =====================================
                # KFINTECH / OTHER REGISTRARS
                # =====================================

                else:

                    for pan in selected_pans:

                        print()
                        print(
                            "Checking PAN:",
                            pan.pan_number
                        )


                        response = check_ipo_allotment(

                            pan.pan_number,

                            selected_ipo_object.registrar,

                            selected_ipo_object.name

                        )


                        name = response.get(
                            "name",
                            ""
                        ).strip()


                        status = response.get(
                            "status",
                            "Unknown"
                        )


                        shares = response.get(
                            "shares",
                            0
                        )


                        # -----------------------------
                        # SAVE NAME
                        # -----------------------------

                        if name:

                            pan.name = name

                            pan.save(
                                update_fields=[
                                    "name"
                                ]
                            )


                        # -----------------------------
                        # DISPLAY NAME
                        # -----------------------------

                        display_name = (

                            name

                            or

                            pan.name

                            or

                            "Name Not Available"

                        )


                        # -----------------------------
                        # SAVE RESULT
                        # -----------------------------

                        Allotment.objects.update_or_create(

                            pan=pan,

                            ipo=selected_ipo_object,

                            defaults={

                                "status": status,

                                "shares": shares

                            }

                        )


                        # -----------------------------
                        # ADD RESULT
                        # -----------------------------

                        results.append({

                            "name": display_name,

                            "status": status,

                            "shares": shares

                        })


                message = (
                    "Allotment check completed."
                )


    # =========================================
    # 5. GET SAVED PANS
    # =========================================

    saved_pans = PAN.objects.all()


    # =========================================
    # 6. GET IPOS
    # =========================================

    ipos = IPO.objects.all()


    # =========================================
    # 7. SEND TO HTML
    # =========================================

    return render(

        request,

        "home.html",

        {

            "saved_pans": saved_pans,

            "selected_pans": selected_pans,

            "selected_ipo": selected_ipo,

            "message": message,

            "results": results,

            "ipos": ipos,

        }

    )