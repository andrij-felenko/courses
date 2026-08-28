// Обмежений набір «уже бачених» ключів; час життя — довший за будь-який ретрай.
class TTLSet {
  private m = new Map<string, number>();
  constructor(private ttlMs: number, private cap = 100_000) {}
  has(k: string): boolean {
    const t = this.m.get(k);
    if (t === undefined) return false;
    if (Date.now() - t > this.ttlMs) { this.m.delete(k); return false; }
    return true;
  }
  add(k: string): void {
    if (this.m.size >= this.cap) this.m.delete(this.m.keys().next().value); // витісняємо найстаріший
    this.m.set(k, Date.now());
  }
}
const seen = new TTLSet(10 * 60_000);  // 10 хв

function countOnce(route: string, client: string, req: Request): void {
  const key = req.header("idempotency-key");
  if (key) {
    const dedupKey = `${client}:${key}`;
    if (seen.has(dedupKey)) return;   // це ретрай — уже пораховано
    seen.add(dedupKey);
  }
  deprCalls.inc({ route, client });
}
