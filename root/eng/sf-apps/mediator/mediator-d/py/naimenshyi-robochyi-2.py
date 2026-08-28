class OrderDialog:                                # КОНКРЕТНИЙ ПОСЕРЕДНИК
    def __init__(self) -> None:
        self.self_pickup = Checkbox(self)         # тримає всіх колег
        self.address = TextField(self)
        self.submit = Button(self)

    def notify(self, sender: Widget, event: str) -> None:   # уся логіка вікна — тут
        if sender is self.self_pickup and event == "toggled":
            self.address.enabled = not self.self_pickup.checked   # самовивіз → адреса зайва
            if self.self_pickup.checked:
                self.address.value = ""
        # кнопка активна, якщо самовивіз АБО адресу вписано
        self.submit.enabled = self.self_pickup.checked or self.address.value.strip() != ""
        self.submit.render()
