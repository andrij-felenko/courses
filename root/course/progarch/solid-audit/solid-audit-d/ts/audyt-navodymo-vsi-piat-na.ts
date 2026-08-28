class AlarmDispatcher {
  handle(ev: SensorEvent) {
    // 1) політика: чи це взагалі тривога?
    if (ev.type !== "motion" || !this.armed) return;
    if (ev.zone === "pet-safe") return;                 // зона, де бігає кіт

    // 2) як це звучить для людини
    const text = `Рух у зоні «${ev.zone}» о ${new Date().toLocaleTimeString()}`;

    // 3) чим шлемо — Twilio SMS, прибитий цвяхом
    const twilio = new TwilioClient(TWILIO_SID, TWILIO_TOKEN);
    twilio.messages.create({ to: this.ownerPhone, body: text });

    // 4) слід — теж прибитий цвяхом, прямо у файл
    fs.appendFileSync("/var/log/alarms.log", text + "\n");
  }
}
