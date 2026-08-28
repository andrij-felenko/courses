import "net/http"

func setSessionCookie(w http.ResponseWriter, token string) {
    http.SetCookie(w, &http.Cookie{
        Name:     "sid",
        Value:    token,
        Path:     "/",
        HttpOnly: true,                 // JS не дістане
        Secure:   true,                 // лише HTTPS
        SameSite: http.SameSiteLaxMode, // щит від CSRF
        MaxAge:   60 * 60 * 24 * 14,    // 14 діб у секундах
    })
}
