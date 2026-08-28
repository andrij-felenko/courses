# Квадратичний закон у насиченні: Id = 0.5 * k * (Vgs - Vth)^2

def id_sat(vgs, vth, k):
    vov = vgs - vth                 # перевищення порогу
    if vov <= 0.0:                  # нижче порога — канал закрито
        return 0.0
    return 0.5 * k * vov * vov      # квадрат перевищення

vth, k = 1.0, 0.5
for vgs in (1.5, 2.0, 3.0):
    vov = vgs - vth
    print(f"Vgs={vgs:.1f} V  Vov={vov:.1f} V  Id={id_sat(vgs, vth, k):.3f} A")
