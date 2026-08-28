import { createHash } from "node:crypto";

class PercentFlags implements Flags {
  constructor(private percentByKey: Map<string, number>) {}

  sampled(key: string, id: string): boolean {
    const pct = this.percentByKey.get(key) ?? 0;   // 0 → вимкнено; 1, 10, 100 — щаблі
    if (pct >= 100) return true;
    if (pct <= 0) return false;
    // Хеш стабільного id → рівномірне число 0..99; те саме id → та сама відповідь
    const h = createHash("sha256").update(`${key}:${id}`).digest();
    const bucket = h.readUInt32BE(0) % 100;
    return bucket < pct;
  }
}
