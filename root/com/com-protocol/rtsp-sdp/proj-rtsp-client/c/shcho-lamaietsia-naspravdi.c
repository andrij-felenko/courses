/* Форма RFC 2069, на яку посилається специфікація RTSP:
     HA1      = MD5(user ":" realm ":" pass)
     HA2      = MD5(method ":" uri)
     response = MD5(HA1 ":" nonce ":" HA2)
   Камера, що прислала qop="auth", хоче довшу форму RFC 2617:
     response = MD5(HA1 ":" nonce ":" nc ":" cnonce ":" qop ":" HA2)
   md5_hex — будь-яка реалізація MD5, що дає 32 шістнадцяткові символи. */
static void digest_header(const char *user, const char *pass, const char *realm,
                          const char *nonce, const char *method, const char *uri,
                          char *out, size_t n) {
    char a1[33], a2[33], resp[33], buf[512];
    snprintf(buf, sizeof buf, "%s:%s:%s", user, realm, pass); md5_hex(buf, a1);
    snprintf(buf, sizeof buf, "%s:%s", method, uri);          md5_hex(buf, a2);
    snprintf(buf, sizeof buf, "%s:%s:%s", a1, nonce, a2);     md5_hex(buf, resp);
    snprintf(out, n, "Authorization: Digest username=\"%s\", realm=\"%s\", "
                     "nonce=\"%s\", uri=\"%s\", response=\"%s\"\r\n",
             user, realm, nonce, uri, resp);
}
