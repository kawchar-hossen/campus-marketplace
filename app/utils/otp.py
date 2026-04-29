# app/utils/otp.py
import random
from datetime import datetime, timedelta

# Temporary in-memory storage (for learning/demo)
otp_store = {}

def generate_otp(email):
    otp = str(random.randint(100000, 999999))

    otp_store[email] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }

    return otp


def verify_otp(email, user_otp):
    data = otp_store.get(email)

    if not data:
        return False

    if datetime.utcnow() > data["expires"]:
        return False

    return data["otp"] == user_otp