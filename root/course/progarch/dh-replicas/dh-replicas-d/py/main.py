import time

LAG_WINDOW = 3.0   # с: консервативна стеля очікуваного лагу реплік

class ReadRouter:
    def __init__(self, leader, followers):
        self.leader = leader
        self.followers = followers
        self.last_write = {}                 # home_id → монотонний час останнього запису сесії

    def note_write(self, home_id: str) -> None:
        # застосунок щойно записав у твін цього дому на лідері
        self.last_write[home_id] = time.monotonic()

    def route(self, home_id: str, kind: str):
        # kind: "lock" | "device_state" | "registry" | "telemetry"
        if kind == "lock":
            return self.leader               # безпека: стан замка завжди з лідера
        if kind == "device_state":
            wrote = self.last_write.get(home_id, -1e9)
            if time.monotonic() - wrote < LAG_WINDOW:
                return self.leader           # read-your-writes: свій свіжий запис — з лідера
            return self._follower(home_id)   # давній/чужий стан — лаг стерпний
        return self._follower(home_id)       # реєстр, телеметрія, історія — лаг нікого не ранить

    def _follower(self, home_id: str):
        # монотонні читання: та сама сесія завжди на ТУ САМУ репліку, щоб час не йшов назад
        return self.followers[hash(home_id) % len(self.followers)]
