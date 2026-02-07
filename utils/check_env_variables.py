import os

def check_env_variables():
    print("GOOGLE_VISION_API =", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    print("GOOGLE_GEMINI_API =", os.environ.get("GEMINI_API_KEY"))
