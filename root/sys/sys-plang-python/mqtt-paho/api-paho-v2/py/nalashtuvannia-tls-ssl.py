client.tls_set(
    ca_certs: str | None = None,
    certfile: str | None = None,
    keyfile: str | None = None,
    cert_reqs: ssl.VerifyMode = ssl.CERT_REQUIRED,
    tls_version: int = ssl.PROTOCOL_TLS_CLIENT,
    ciphers: str | None = None,
    keyfile_password: str | None = None
) -> None

client.tls_set_context(context: ssl.SSLContext) -> None
client.tls_insecure_set(value: bool) -> None
