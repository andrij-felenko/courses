// Фаза 2 strangler-fig: та сама форма TelemetrySink, за нею — обидва шляхи.
class MigratingSink implements TelemetrySink {
  constructor(private oldSink: TelemetrySink, private newSink: TelemetrySink) {}

  async record(e: DeviceEvent): Promise<void> {
    await this.oldSink.record(e);            // джерело правди — поки старе
    try {
      await this.newSink.record(e);          // новий шлях прогріваємо паралельно
    } catch (err) {
      metrics.increment("telemetry.shadow_write_failed");   // не валимо запис
    }
  }
}
