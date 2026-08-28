// ПРИМІТИВ 3 — журнал подій.  Суть: незмінна впорядкована стрічка +
// у КОЖНОГО читача свій offset; кожен гортає у своєму темпі, нікому не заважаючи.
class EventLog<T> {
  private entries: T[] = [];
  private offset = new Map<string, number>();      // ім'я читача → доки ВІН дочитав
  append(m: T): void { this.entries.push(m); }
  read(reader: string): T[] {
    const from = this.offset.get(reader) ?? 0;
    const fresh = this.entries.slice(from);
    this.offset.set(reader, this.entries.length);   // просунули курсор САМЕ цього читача
    return fresh;
  }
  replay(): T[] { return this.entries.slice(); }    // переграти з початку — стрічка ціла
}
