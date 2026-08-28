@dataclass(frozen=True)
class Snapshot:
    stream_id: str
    version: int            # до якої версії потоку враховано події
    state: Account          # згорнутий стан рівно на цю версію

# Кеш знімків: останній знімок на потік. У реальності — окрема таблиця/сховище.
class SnapshotStore:
    def __init__(self):
        self._snaps: dict[str, Snapshot] = {}
    def latest(self, stream_id: str) -> Snapshot | None:
        return self._snaps.get(stream_id)
    def save(self, s: Snapshot) -> None:
        self._snaps[s.stream_id] = s

# Відбудова стану ЗІ знімком: беремо базу зі знімка й докладаємо лише хвіст.
def load_state(store: EventStore, snaps: SnapshotStore, stream_id: str) -> Account:
    snap = snaps.latest(stream_id)
    base_state = snap.state if snap else EMPTY
    from_version = snap.version if snap else 0

    stream = store.read(stream_id)
    tail = stream[from_version:]                 # події ПІСЛЯ знімка — короткий хвіст
    state = base_state
    for st in tail:
        state = apply(state, st.event)
    return state

# Політика знімкування: раз на SNAP_EVERY подій кладемо свіжий знімок.
SNAP_EVERY = 100

def maybe_snapshot(store: EventStore, snaps: SnapshotStore, stream_id: str) -> None:
    version = store.current_version(stream_id)
    last = snaps.latest(stream_id)
    since = version - (last.version if last else 0)
    if since >= SNAP_EVERY:
        # Порахувати актуальний стан (через знімок — дешево) і зберегти як новий знімок.
        state = load_state(store, snaps, stream_id)
        snaps.save(Snapshot(stream_id, version, state))
