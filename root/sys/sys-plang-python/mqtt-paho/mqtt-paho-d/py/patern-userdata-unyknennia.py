class TelemetryReceiver:
    def __init__(self, broker_url: str):
        self.stats = {"received": 0, "errors": 0}
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            userdata=self.stats
        )
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, message):
        userdata["received"] += 1
