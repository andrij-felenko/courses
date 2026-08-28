import time

# --- тонкий шар приладу (SCPI текстом у порт) ---
# port_send(line)  — дописує "\n" і шле в UART (pyserial)
# port_query(line) — шле запит, парсить число з відповіді

def psu_set_voltage(v):  port_send(f"VOLT {v:.3f}")
def load_set_current(a): port_send(f"CURR {a:.3f}")

# один вузол сітки: повертає ккд у % (або -1 при відмові DUT)
def measure_point(vin_set, iout_set, vout_nom):
    psu_set_voltage(vin_set);   port_send("OUTP ON")      # вхід під напругою
    load_set_current(iout_set); port_send("INP ON")       # навантаження тримає струм

    time.sleep(2.0)             # ЧЕКАТИ усталення: електрика + тепловий дрейф

    vin  = port_query("MEAS:VOLT? PSU")   # Kelvin-відбір — окремі дроти на клемах
    iin  = port_query("MEAS:CURR? PSU")
    vout = port_query("MEAS:VOLT? LOAD")
    iout = port_query("MEAS:CURR? LOAD")

    if vout < vout_nom * 0.9:             # вихід просів > 10 % → DUT у захисті/відмові
        port_send("INP OFF")             # негайно зняти струм, не палити плату
        return -1.0

    pin, pout = vin * iin, vout * iout
    return (pout / pin) * 100.0 if pin > 0.0 else -1.0
