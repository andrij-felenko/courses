def report(name, m, Cd, A, marks):
    vt = terminal(m, Cd, A)
    print(f"\n{name}:  v_t = {vt:.1f} м/с  ({vt*3.6:.0f} км/год)")
    print("   t, с | v (повітря) | v = g·t (вакуум)")
    marks = iter(sorted(marks)); target = next(marks)
    for t, v in fall(m, Cd, A):
        if t >= target:
            print(f"  {t:5.1f} | {v:9.2f}   | {g*t:9.1f}")
            try: target = next(marks)
            except StopIteration: break

# Парашутист «пузом донизу»
report("Парашутист", m=80, Cd=0.9, A=0.50, marks=[2, 5, 10, 20])

# Дощова крапля: масу й переріз рахуємо з радіуса кулі
r = 0.002                           # м, велика крапля (≈4 мм у діаметрі)
m_drop = 1000 * (4/3)*math.pi*r**3  # вода, ρ_w = 1000 кг/м³
A_drop = math.pi*r**2
report("Дощова крапля", m=m_drop, Cd=0.47, A=A_drop, marks=[0.5, 1, 2, 3])
