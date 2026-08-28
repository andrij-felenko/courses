client.connect(
    host: str,
    port: int = 1883,
    keepalive: int = 60,
    bind_address: str = "",
    bind_port: int = 0,
    clean_start: bool = MQTT_CLEAN_START_FIRST_ONLY,
    properties: Properties | None = None
) -> ReasonCode

client.connect_async(
    host: str,
    port: int = 1883,
    keepalive: int = 60,
    bind_address: str = "",
    bind_port: int = 0,
    clean_start: bool = MQTT_CLEAN_START_FIRST_ONLY,
    properties: Properties | None = None
) -> None
