// Порт — та сама форма, що й у гексагоні v2. Логіка хаба знає лише його.
interface CloudLink {
  send(cmd: Command): Promise<Result>;
}

// Адаптер v2: сусід у тому ж процесі. Дві долі — повернув або кинув.
class InProcessCloud implements CloudLink {
  send(cmd: Command) { return this.cloud.handle(cmd); }   // все-або-нічого
}

// Адаптер за межею машини: та сама форма, але за нею — мережа.
// Уся чесність зібрана ТУТ, логіка над портом її не бачить.
class NetworkCloud implements CloudLink {
  async send(cmd: Command): Promise<Result> {
    const key = cmd.id;                    // один ключ на команду — крізь усі повтори
    const deadline = monotonic() + 10_000; // бюджет часу: чекання зі стелею
    return withRetries(deadline, () =>     // повтор із відступом + розкидом
      this.http.post("/cmd", cmd, key, deadline));   // а дублі впізнає бік хмари
  }
}
