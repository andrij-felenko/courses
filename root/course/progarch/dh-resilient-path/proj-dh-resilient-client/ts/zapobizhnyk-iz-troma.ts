// Запобіжник: closed → open → half. Рішення "пускати?" СИНХРОННЕ (без await),
// тому в однопотоковому рушії проба гарантовано одна.
class CircuitOpen extends Error { readonly retryable = false; }
type BState = "closed" | "open" | "half";
const now = () => performance.now();     // МОНОТОННИЙ годинник, не Date.now()

class CircuitBreaker {
  private state: BState = "closed";
  private fails = 0;
  private openedAt = 0;
  private probeInFlight = false;

  constructor(private readonly o: { failsToOpen: number; cooldown: number }) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (!this.allow()) throw new CircuitOpen();   // відкритий → НЕ кличемо, миттєво нагору
    try {
      const r = await fn();
      this.onSuccess();
      return r;
    } catch (e) {
      this.onFailure();                            // рахуємо ЦЕЙ виклик як відмову
      throw e;
    }
  }

  private allow(): boolean {
    if (this.state === "closed") return true;
    if (this.state === "open") {
      if (now() - this.openedAt < this.o.cooldown) return false;   // ще холонемо
      this.state = "half"; this.probeInFlight = true; return true; // ця спроба — і є проба
    }
    if (this.probeInFlight) return false;          // half: пробу вже взяли — решту коротимо
    this.probeInFlight = true; return true;
  }

  private onSuccess() { this.state = "closed"; this.fails = 0; this.probeInFlight = false; }

  private onFailure() {
    if (this.state === "half") return this.open();          // проба впала — знову відкрито
    if (++this.fails >= this.o.failsToOpen) this.open();
  }

  private open() { this.state = "open"; this.openedAt = now(); this.fails = 0; this.probeInFlight = false; }
}
