interface Snapshot {
  streamId: string;
  version: number;        // до якої версії потоку враховано події
  state: Account;         // згорнутий стан рівно на цю версію
}

// Кеш знімків: останній знімок на потік. У реальності — окрема таблиця/сховище.
class SnapshotStore {
  private snaps = new Map<string, Snapshot>();
  latest(streamId: string): Snapshot | undefined { return this.snaps.get(streamId); }
  save(s: Snapshot): void { this.snaps.set(s.streamId, s); }
}

// Відбудова стану ЗІ знімком: беремо базу зі знімка й докладаємо лише хвіст.
function loadState(store: EventStore, snaps: SnapshotStore, streamId: string): Account {
  const snap = snaps.latest(streamId);
  const baseState = snap ? snap.state : EMPTY;
  const fromVersion = snap ? snap.version : 0;

  const stream = store.read(streamId);
  const tail = stream.slice(fromVersion);       // події ПІСЛЯ знімка — короткий хвіст
  return tail.reduce((s, st) => apply(s, st.event), baseState);
}

// Політика знімкування: раз на SNAP_EVERY подій кладемо свіжий знімок.
const SNAP_EVERY = 100;

function maybeSnapshot(store: EventStore, snaps: SnapshotStore, streamId: string): void {
  const version = store.currentVersion(streamId);
  const last = snaps.latest(streamId);
  const since = version - (last ? last.version : 0);
  if (since >= SNAP_EVERY) {
    // Порахувати актуальний стан (через знімок — дешево) і зберегти як новий знімок.
    const state = loadState(store, snaps, streamId);
    snaps.save({ streamId, version, state });
  }
}
