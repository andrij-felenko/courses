class TokenBucket {
  private tokens: number;
  private last: number;                        // мітка МОНОТОННОГО годинника, мс
  constructor(private capacity: number,        // b — скільки можна поспіль
              private refillPerSec: number,     // r — усталений темп
              now: number) {
    this.tokens = capacity;
    this.last = now;
  }
  // true й списує жетон, якщо він є; false — відро порожнє.
  allow(now: number): boolean {
    const gained = ((now - this.last) / 1000) * this.refillPerSec;
    this.tokens = Math.min(this.capacity, this.tokens + gained);
    this.last = now;
    if (this.tokens >= 1) { this.tokens -= 1; return true; }
    return false;                              // порожньо → притримати / злити / відкинути
  }
}
