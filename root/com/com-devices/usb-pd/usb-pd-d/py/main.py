# callback: контролер віддав меню Source_Capabilities (масив PDO)
def sink_negotiate(pdos):
    V_WANT_MV = 20_000                       # потрібні 20 В
    fits = [p for p in pdos                  # перебрати меню
            if p.type == PDO_FIXED and p.voltage_mv <= V_WANT_MV]  # не вище за стелю пристрою
    if not fits:
        return False                         # нічого не лягло → лишаємось на 5 В
    best = max(fits, key=lambda p: p.voltage_mv)  # лишити найвищий придатний

    pd.send_request(best.index, operating_ma=3000)  # Request: цей профіль, робочий струм 3 А
    if pd.wait_accept(timeout_ms=50) != PD_ACCEPT:  # джерело має відповісти Accept у межах таймауту
        return False                         # відмова → контракт не укладено, 5 В
    pd.wait_event(PD_PS_RDY)                  # PS_RDY: нова напруга на VBUS стоїть
    return True                              # тепер на VBUS 20 В — контракт діє
