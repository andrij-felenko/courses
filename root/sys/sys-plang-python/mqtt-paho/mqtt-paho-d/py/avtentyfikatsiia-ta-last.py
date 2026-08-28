# Передача облікових даних
client.username_pw_set("telemetry_service_01", "SecureServiceToken_XYZ")

# Заповіт LWT: брокер надішле це повідомлення в топік при нештатному розриві сесії
client.will_set(
    topic="services/ingestion-srv-01/status",
    payload=b'{"state": "crashed", "node": "srv-prod-01"}',
    qos=1,
    retain=True
)
