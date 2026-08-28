# ── Один лідер: усі записи серіалізуються в одному місці ──
class SingleLeader:
    def __init__(self): self.value = None
    def write(self, v): self.value = v      # лягає ПОВЕРХ попереднього
    def read(self):     return self.value   # завжди рівно одне значення

leader = SingleLeader()
leader.write("off")        # застосунок вимкнув обігрівач
leader.write("on")         # автоматизація ввімкнула — ПІЗНІШЕ, побачивши "off"
print(leader.read())       # -> "on"   одна історія, конфлікту нема за побудовою

# ── Кілька писарів: два вузли приймають запис у той самий ключ ──
class Replica:
    def __init__(self, name): self.name, self.value = name, None
    def write(self, v):       self.value = v

a, b = Replica("A"), Replica("B")
a.write("off")             # застосунок пише у вузол свого регіону
b.write("on")              # хаб пише в інший вузол — у ту саму мить, не бачачи A
# репліки синхронізуються й виявляють: обидва змінили ключ НЕЗАЛЕЖНО
versions = {a.value, b.value}      # -> {"off", "on"} — дві живі версії
assert len(versions) == 2          # жодна не "пізніша" → конфлікт, машина не розсудить
