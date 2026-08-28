# ── 2. ЖИВА СЕСІЯ ДОМУ (актор): кеш-координатор над рядком, НЕ джерело правди ──
from collections import deque

class HomeSession:
    def __init__(self, home_id: str, store: ShardStore, audit: AuditLog):
        self.home_id = home_id
        self._store, self._audit = store, audit
        self._twin: Twin | None = None    # порожньо, доки не гідратуємось
        self._box = deque()               # пошта: серіалізує команди дому
        self._busy = False

    # ГІДРАТАЦІЯ: наповнити сесію станом із ДЖЕРЕЛА ПРАВДИ при виході на зв'язок
    def hydrate(self) -> None:
        self._twin = self._store.get(self.home_id)     # ← увесь «відновлення стану»

    # ЄДИНИЙ вхід для команд: покласти в пошту й розбудити цикл
    def tell(self, cmd: dict) -> None:
        self._box.append(cmd); self._pump()

    def _pump(self) -> None:
        if self._busy:                    # вже крутиться — новий tell лише долив у чергу
            return
        self._busy = True
        while self._box:                  # одне за раз, до кінця
            self._apply(self._box.popleft())
        self._busy = False

    def _apply(self, cmd: dict) -> None:
        assert self._twin is not None, "сесію не гідратовано"
        # (a) новий стан у кеші — версія росте
        nxt = replace(self._twin,
                      version=self._twin.version + 1,
                      bolt="locked" if cmd["kind"] == "lock" else "unlocked",
                      last_cmd=f'{cmd["by"]}#{cmd["seq"]}')
        # (b) НАСКРІЗНИЙ запис у ДЖЕРЕЛО ПРАВДИ (CAS по version)
        if not self._store.put_cas(nxt, self._twin.version):
            self.hydrate()               # хтось випередив → перечитати правду…
            return self._apply(cmd)      # …і повторити команду на свіжому стані
        # (c) дописати ФАКТ у журнал аудиту (лише замки)
        self._audit.append(LockEvent(self.home_id, nxt.bolt, cmd["by"], time.time()))
        # (d) аж ТЕПЕР зафіксувати кеш → read-your-writes: кеш == довговічний рядок
        self._twin = nxt

    def snapshot(self) -> Twin:          # тепле читання: з живого актора
        return self._twin
