function sessionCookie(token: string): string {
  const twoWeeks = 60 * 60 * 24 * 14; // секунд
  return [
    `sid=${token}`,
    "HttpOnly",       // недосяжна для document.cookie
    "Secure",         // лише поверх HTTPS
    "SameSite=Lax",   // не піде на чужий POST → щит від CSRF
    "Path=/",
    `Max-Age=${twoWeeks}`,
  ].join("; ");
}

// у обробнику входу:
res.setHeader("Set-Cookie", sessionCookie(token));
