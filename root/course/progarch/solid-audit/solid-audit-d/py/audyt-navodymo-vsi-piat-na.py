class AlarmDispatcher:
    def handle(self, ev: SensorEvent) -> None:
        # 1) політика: чи це взагалі тривога?
        if ev.type != "motion" or not self.armed:
            return
        if ev.zone == "pet-safe":                        # зона, де бігає кіт
            return

        # 2) як це звучить для людини
        text = f"Рух у зоні «{ev.zone}» о {datetime.now():%H:%M:%S}"

        # 3) чим шлемо — Twilio SMS, прибитий цвяхом
        twilio = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
        twilio.messages.create(to=self.owner_phone, body=text)

        # 4) слід — теж прибитий цвяхом, прямо у файл
        with open("/var/log/alarms.log", "a") as f:
            f.write(text + "\n")
