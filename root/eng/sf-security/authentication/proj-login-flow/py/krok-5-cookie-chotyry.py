def session_cookie(token: str) -> str:
    two_weeks = 60 * 60 * 24 * 14  # секунд
    return "; ".join([
        f"sid={token}",
        "HttpOnly",       # недосяжна для document.cookie
        "Secure",         # лише поверх HTTPS
        "SameSite=Lax",   # щит від CSRF
        "Path=/",
        f"Max-Age={two_weeks}",
    ])

# у Flask те саме роблять напряму:
# resp.set_cookie("sid", token, httponly=True, secure=True,
#                 samesite="Lax", max_age=two_weeks, path="/")
