class paho.mqtt.client.Client(
    callback_api_version: CallbackAPIVersion,
    client_id: str = "",
    clean_session: bool | None = None,
    userdata: Any = None,
    protocol: int = MQTTv311,
    transport: str = "tcp",
    reconnect_on_failure: bool = True,
    manual_ack: bool = False
)
