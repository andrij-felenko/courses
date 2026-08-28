# Локальне керування домом — НЕ потребує ні хмари, ні кворуму.
class Hub:
    def __init__(self, edge: Replica):
        self.edge = edge
        self._telemetry = []
    def toggle_light(self, on: bool) -> str:
        return f"лампу {'увімкнено' if on else 'вимкнено'} локально"
    def record_temp(self, key: str, celsius: float) -> None:
        self._telemetry.append((key, celsius))
    def backlog(self) -> int:
        return len(self._telemetry)

a, b, edge = Replica("A"), Replica("B"), Replica("E·край")
cloud = Cluster([a, b, edge], a, lambda to: 1 if to is b else 5)
GK = "grant:home-42:guest"
cloud.write(GK, True); cloud.advance(10)    # усі копії: v1(True) — доступ виданий

edge.linked = False                          # РОЗКОЛ: край відрізано від хмари

cloud.write(GK, False); cloud.advance(10)    # у хмарі відкликано (a,b → v2); до краю НЕ доходить

# Дім живе локально: хаб керує пристроями й копить телеметрію в чергу.
hub = Hub(edge)
print("хаб:", hub.toggle_light(True))               # працює без хмари
hub.record_temp("temp:home-42:kitchen", 21.4)
print("телеметрія в черзі:", hub.backlog())         # доллється потім

# Ворота на боці хаба: доступна ЛИШЕ застаріла edge.
print("край локально каже:", read_eventual(GK, edge).value)   # True — ЗАСТАРІЛЕ!
print("ворота (строго, лише край):",
      "ВІДЧИНИТИ" if may_open(GK, [edge]) else "ВІДМОВА")       # fail-closed
print("ворота (строго, хмара):",
      "ВІДЧИНИТИ" if may_open(GK, [a, b]) else "ВІДМОВА")       # бачить v2
