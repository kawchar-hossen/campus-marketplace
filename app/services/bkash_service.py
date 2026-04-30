import random
from flask import session

def generate_bkash_otp(phone):
    otp = str(random.randint(100000, 999999))

    session["bkash_otp"] = {
        "phone": phone,
        "otp": otp
    }

    return otp


def verify_bkash_otp(phone, otp):
    data = session.get("bkash_otp")

    if not data:
        return False

    if data["phone"] != phone:
        return False

    if data["otp"] != otp:
        return False

    session.pop("bkash_otp", None)
    return True