// Тіло події — доконаний факт. Мінімум полів: що і на скільки.
type AccountEvent =
  | { kind: "Deposited"; amount: number }
  | { kind: "Withdrawn"; amount: number }
  | { kind: "FeeCharged"; amount: number };

// Збережена подія = тіло + метадані потоку. version — позиція в потоці (з 1).
interface Stored {
  streamId: string;
  version: number;        // 1, 2, 3, … — монотонно росте в межах потоку
  event: AccountEvent;
  at: string;             // мітка часу, знадобиться темпоральним запитам
}

// Сигнал конфлікту версій — окремий тип, щоб виклик міг його спіймати й повторити.
class VersionConflict extends Error {
  constructor(public expected: number, public actual: number) {
    super(`очікували версію ${expected}, а потік уже на ${actual}`);
  }
}

class EventStore {
  // У реальності — таблиця (stream_id, version, payload) з PK (stream_id, version).
  // Тут — просто масив на потік.
  private streams = new Map<string, Stored[]>();

  // Прочитати весь потік (для згортання й для перевірки версії).
  read(streamId: string): Stored[] {
    return this.streams.get(streamId) ?? [];
  }

  // Поточна версія потоку = скільки в ньому подій.
  currentVersion(streamId: string): number {
    return this.read(streamId).length;
  }

  // ОСЕРДЯ append-only. Дописати нові події ТІЛЬКИ якщо потік досі на expectedVersion.
  append(streamId: string, expectedVersion: number, events: AccountEvent[]): Stored[] {
    const stream = this.streams.get(streamId) ?? [];
    const actual = stream.length;
    if (actual !== expectedVersion) {
      // Хтось дописав між нашим читанням і цим записом — відхиляємо, хай повторить.
      throw new VersionConflict(expectedVersion, actual);
    }
    const now = new Date().toISOString();
    const appended = events.map((event, i) => ({
      streamId, version: actual + i + 1, event, at: now,
    }));
    this.streams.set(streamId, [...stream, ...appended]);
    return appended;                 // ніколи не міняємо старе — лише додаємо
  }
}
