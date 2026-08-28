A, B, E = Replica("A·лідер"), Replica("B·репліка"), Replica("E·край")
cluster = Cluster([A, B, E], A, lambda to: 1 if to is B else 5)   # E лагає вп'ятеро

KEY = "grant:home-42:pidryadnyk"
cluster.write(KEY, True)           # власник видав доступ → версія 1
cluster.advance(10)                # усі копії наздогнали: A, B, E = v1(True)

# T0: власник ВІДКЛИКАЄ доступ.
cluster.write(KEY, False)          # → версія 2, лягає на A негайно
cluster.advance(2)                 # 2 тики: B (лаг 1) уже має v2, E (лаг 5) — ще ні

# T1: підрядник тягне двері. Той самий факт, дві дороги читання.
# Навмисне беремо кворум БЕЗ лідера — {B, E} — і все одно ловимо відкликання.
print("строго {B,E}:", "ВІДЧИНИТИ" if may_open(KEY, [B, E]) else "ВІДМОВА")
stale = read_eventual(KEY, E)
print("зрештою E:  ", "ВІДЧИНИТИ" if stale and stale.value is True else "ВІДМОВА",
      f"(версія {stale.version})")

cluster.advance(4)                 # E наздоганяє (лаг 5 від T0)
now = read_eventual(KEY, E)
print("зрештою E, збіжність:", "ВІДЧИНИТИ" if now and now.value is True else "ВІДМОВА",
      f"(версія {now.version})")
