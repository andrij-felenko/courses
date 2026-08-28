enum Severity { Info, Warning, Critical }

interface Notification {
  recipient: string;
  event: string;    // ідентичність події: "door-open@2026-07-11T07:14"
  cls: string;      // тема для злиття
  channel: string;
  severity: Severity;
  at: number;       // час події, ms
  holds?: number;
}

type Decision = { outcome: "delivered" | "buffered" | "dropped"; reason: string };

class Gate {
  async admit(n: Notification): Promise<Decision> {
    // 0. Критичне — в обхід усього; дедуп навмисне НЕ робимо.
    if (n.severity === Severity.Critical) {
      await this.deliver(n);
      return { outcome: "delivered", reason: "critical-bypass" };
    }

    // 1. Дедуп: SET dk NX PX ttl → false, якщо ключ уже є.
    const first = await this.store.setNX(dedupKey(n), this.dedupTTL(n));
    if (!first) return { outcome: "dropped", reason: "duplicate" };

    // 2. Злиття: RPUSH у групу; довжина 1 ⇒ ми власник таймера.
    const size = await this.store.append(groupKey(n), JSON.stringify(n), 2 * this.window);
    if (size === 1) this.arm(groupKey(n), n.cls);
    return { outcome: "buffered", reason: "coalescing" };
  }
}
