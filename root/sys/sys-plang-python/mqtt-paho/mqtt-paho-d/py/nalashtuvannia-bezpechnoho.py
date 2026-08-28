import ssl

# Варіант 1: Спрощений через tls_set()
client.tls_set(
    ca_certs="/etc/ssl/certs/internal-ca.crt",
    certfile="/etc/ssl/certs/backend-client.crt",  # Для mTLS
    keyfile="/etc/ssl/private/backend-client.key",  # Для mTLS
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT
)

# Варіант 2: Пряма передача ssl.SSLContext (рекомендовано для production)
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile="/etc/ssl/certs/internal-ca.crt")
context.load_cert_chain(
    certfile="/etc/ssl/certs/backend-client.crt",
    keyfile="/etc/ssl/private/backend-client.key"
)
context.check_hostname = True
context.verify_mode = ssl.CERT_REQUIRED

client.tls_set_context(context)
