def on_subscribe(
    client: Client,
    userdata: Any,
    mid: int,
    reason_codes: list[ReasonCode],
    properties: Properties | None
) -> None

def on_unsubscribe(
    client: Client,
    userdata: Any,
    mid: int,
    reason_codes: list[ReasonCode],
    properties: Properties | None
) -> None
