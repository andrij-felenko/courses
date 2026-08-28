# Уся прив'язка до постачальника A замкнена ТУТ.
# Жоден інший файл не бачить vendora.
class VendorAQueue(MessageQueue):
    def __init__(self, url: str) -> None:
        self._cli = vendora.Client(url)  # тип вендора — лише всередині

    def publish(self, topic: str, payload: str) -> None:
        m = vendora.Message()            # деталь вендора не витікає назовні
        m.channel = topic
        m.body = payload
        if self._cli.send(m) != vendora.OK:
            raise RuntimeError("vendorA publish failed")

    def consume(self, timeout_ms: int) -> str | None:
        m = vendora.Message()
        if self._cli.poll(m, timeout_ms) != vendora.OK:
            return None
        return m.body
