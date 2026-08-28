// app: після операції злити події й розіслати. Пристрій НЕ знає про підписників.
type Handler = (e: DomainEvent) => void;

class EventBus {
  private handlers: Handler[] = [];
  subscribe(h: Handler) { this.handlers.push(h); }
  publish(events: DomainEvent[]) {
    for (const e of events) for (const h of this.handlers) h(e);
  }
}

// Контекст білінгу: пристрій «активний» від commission до retire — за це й рахунок.
class Billing {
  active = new Set<string>();
  on = (e: DomainEvent) => {
    if (e.kind === "DeviceCommissioned") this.active.add(e.deviceId);
    if (e.kind === "DeviceRetired")      this.active.delete(e.deviceId);
  };
}
// Контекст телеметрії: приймає покази, поки пристрій не списаний.
class Telemetry {
  accepting = new Set<string>();
  on = (e: DomainEvent) => {
    if (e.kind === "DeviceCommissioned") this.accepting.add(e.deviceId);
    if (e.kind === "DeviceRetired")      this.accepting.delete(e.deviceId);
  };
}

const bus = new EventBus();
const billing = new Billing(), telemetry = new Telemetry();
bus.subscribe(billing.on); bus.subscribe(telemetry.on);

const d = new Device("lock-42");
d.commission("home-7"); bus.publish(d.pullEvents());  // білінг +1, телеметрія приймає
d.markOffline();        bus.publish(d.pullEvents());  // телеметрія ДОСІ приймає: offline ≠ retired
d.retire();             bus.publish(d.pullEvents());  // білінг −1, телеметрія глушить прийом
