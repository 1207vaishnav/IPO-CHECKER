import requests

from .models import IPO
from .mufg_service import check_mufg_multiple


# =========================================
# MAIN REGISTRAR FUNCTION
# =========================================

def check_ipo_allotment(
    pan_number,
    registrar,
    ipo_name
):

    # =========================================
    # KFINTECH
    # =========================================

    if registrar == "KFintech":

        return check_kfintech(
            pan_number,
            ipo_name
        )


    # =========================================
    # MUFG INTIME
    # =========================================

    elif registrar == "MUFG Intime":

        return check_mufg(
            pan_number,
            ipo_name
        )


    # =========================================
    # UNSUPPORTED
    # =========================================

    return {

        "status": "Unsupported Registrar",

        "shares": 0,

        "name": ""

    }


# =========================================
# KFINTECH
# =========================================

def check_kfintech(
    pan_number,
    ipo_name
):

    # -------------------------------------
    # Find IPO
    # -------------------------------------

    try:

        ipo = IPO.objects.get(
            name=ipo_name
        )

    except IPO.DoesNotExist:

        return {

            "status": "IPO Not Found",

            "shares": 0,

            "name": ""

        }


    # -------------------------------------
    # Get KFintech client ID
    # -------------------------------------

    client_id = getattr(
        ipo,
        "client_id",
        None
    )


    if not client_id:

        return {

            "status": "KFintech Client ID Missing",

            "shares": 0,

            "name": ""

        }


    # -------------------------------------
    # KFintech API
    # -------------------------------------

    url = (
        "https://0uz601ms56.execute-api."
        "ap-south-1.amazonaws.com/prod/api/query"
    )


    # -------------------------------------
    # Headers
    # -------------------------------------

    headers = {

        "accept": (
            "application/json, "
            "text/plain, */*"
        ),

        "client_id": str(
            client_id
        ),

        "reqparam": (
            pan_number
            .strip()
            .upper()
        ),

    }


    # -------------------------------------
    # Parameters
    # -------------------------------------

    params = {

        "type": "pan"

    }


    # -------------------------------------
    # Request
    # -------------------------------------

    try:

        response = requests.get(

            url,

            headers=headers,

            params=params,

            timeout=20

        )

        response.raise_for_status()

        result = response.json()


    except requests.RequestException as e:

        print(
            "KFintech Request Error:",
            e
        )

        return {

            "status": "KFintech Request Failed",

            "shares": 0,

            "name": ""

        }


    except ValueError as e:

        print(
            "KFintech JSON Error:",
            e
        )

        return {

            "status": "Invalid KFintech Response",

            "shares": 0,

            "name": ""

        }


    # -------------------------------------
    # Get data
    # -------------------------------------

    data = result.get(
        "data",
        []
    )


    if not data:

        return {

            "status": "Not Found",

            "shares": 0,

            "name": ""

        }


    # -------------------------------------
    # First result
    # -------------------------------------

    allotment_data = data[0]


    # -------------------------------------
    # Get applicant name
    # -------------------------------------

    name = (

        allotment_data.get(
            "Name",
            ""
        )

        or

        allotment_data.get(
            "Applicant_Name",
            ""
        )

        or

        allotment_data.get(
            "ApplicantName",
            ""
        )

        or

        ""

    )


    name = str(
        name
    ).strip()


    # -------------------------------------
    # Get allotted shares
    # -------------------------------------

    try:

        shares = int(

            str(

                allotment_data.get(
                    "All_Shares",
                    "0"
                )

            )
            .replace(",", "")
            .strip()

            or "0"

        )

    except (
        ValueError,
        TypeError
    ):

        shares = 0


    # -------------------------------------
    # Determine status
    # -------------------------------------

    if shares > 0:

        status = "Allotted"

    else:

        status = "Not Allotted"


    # -------------------------------------
    # Return result
    # -------------------------------------

    return {

        "name": name,

        "status": status,

        "shares": shares

    }