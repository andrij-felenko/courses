// twin.ts — присутність не переживає домовленого вікна
export const RETENTION_MS = 24 * 60 * 60 * 1000;   // міра з ADR: 24 год

type Event = { ts: number; present: boolean };

export class Twin {
  private events: Event[] = [];
  record(ts: number, present: boolean) { this.events.push({ ts, present }); }
  prune(now: number) {
    const cutoff = now - RETENTION_MS;
    this.events = this.events.filter(e => e.ts >= cutoff);
  }
  presenceSince(cutoff: number): Event[] {          // публічний шлях читання
    return this.events.filter(e => e.ts >= cutoff);
  }
}
