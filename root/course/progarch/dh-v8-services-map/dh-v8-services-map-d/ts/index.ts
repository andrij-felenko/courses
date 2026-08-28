// Порт — стик телеметрії з рештою. Форма та сама, хоч у моноліті, хоч у сервісі.
interface TelemetrySink {
  record(e: DeviceEvent): Promise<void>;
}

// Було, у моноліті: сусідній модуль у тому ж процесі — виклик у пам'яті.
class InProcessSink implements TelemetrySink {
  async record(e: DeviceEvent) { this.store.append(e); }   // наносекунди, все-або-нічого
}

// Стало, після розрізу: той самий порт, але за ним — окремий сервіс за мережею.
// Уся мережева чесність зібрана ТУТ; ядро над портом її не бачить.
class RemoteSink implements TelemetrySink {
  async record(e: DeviceEvent) {
    await this.bus.publish("telemetry", e);   // асинхронно, «щонайменше раз» + дедуп за ключем
  }
}
