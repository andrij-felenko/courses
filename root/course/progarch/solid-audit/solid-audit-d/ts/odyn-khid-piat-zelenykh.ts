interface Notifier { send(msg: Message): Promise<void>; }   // вузька абстракція: рівно одна дія
interface Clock    { now(): Date; }

// Стабільне ядро — чиста політика, і нічого крім неї
class AlarmPolicy {
  constructor(private notify: Notifier, private clock: Clock) {}   // деталі подано ЗЗОВНІ
  handle(ev: SensorEvent): void {
    if (ev.type !== "motion" || !this.armed) return;
    if (ev.zone === "pet-safe") return;
    const t = this.clock.now().toLocaleTimeString();
    this.notify.send({ to: "owner", body: `Рух у зоні «${ev.zone}» о ${t}` });
  }
}

// Волатильні деталі — окремі адаптери. Twilio живе ТУТ, і лише тут.
class SmsNotifier  implements Notifier { /* Twilio всередині */ async send(m){ /*…*/ } }
class PushNotifier implements Notifier { /* канал застосунку */ async send(m){ /*…*/ } }
