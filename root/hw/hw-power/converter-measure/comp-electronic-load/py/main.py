import time

# load — інтерфейс до електронного навантаження (CC);
# in_  — вимір ВХОДУ перетворювача (друге джерело даних).
# Крокуємо струм від 0.5 до 4.0 А по 0.5 А і друкуємо ККД.
iset = 0.5
while iset <= 4.0 + 1e-3:
    load.set_current(iset)     # уставка струму CC: контур притисне MOSFET
    time.sleep(0.200)          # даємо джерелу й контуру усталитися

    vout = load.read_voltage()          # напруга на клемах джерела
    iact = load.read_current()          # реальний струм (≈ iset)
    pout = vout * iact                  # вихідна потужність

    pin = in_.voltage() * in_.current()  # вхідна потужність
    eff = pout / pin if pin > 0.0 else 0.0

    print(f"I={iact:.2f} A  Vout={vout:.3f} V  "
          f"Pout={pout:.2f} W  eff={eff * 100.0:.1f} %")

    iset += 0.5

load.set_current(0.0)          # прибрати навантаження наприкінці
