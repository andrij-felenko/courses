client.subscribe(
    topic: str | tuple[str, int | SubscribeOptions] | list[tuple[str, int | SubscribeOptions]],
    qos: int = 0,
    options: SubscribeOptions | None = None,
    properties: Properties | None = None
) -> tuple[ReasonCode, int]

client.unsubscribe(
    topic: str | list[str],
    properties: Properties | None = None
) -> tuple[ReasonCode, int]
