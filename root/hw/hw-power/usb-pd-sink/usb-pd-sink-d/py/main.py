# callback: контролер віддав меню Source_Capabilities (масив PDO)
def sink_pick_profile(pdos):
    V_MAX_MV = 12_000                        # стеля пристрою: понад 12 В брати НЕ можна
    fits = [p for p in pdos                  # перебрати всі рядки меню
            if p.type == PDO_FIXED and p.voltage_mv <= V_MAX_MV]  # тільки придатні
    if not fits:
        return False                         # нічого не лягло → лишаємось на 5 В
    best = max(fits, key=lambda p: p.voltage_mv)  # лишити найвищий придатний

    pd.send_request(best.index, operating_ma=2000)  # Request: цей профіль, робочий струм 2 А
    if pd.wait_accept(timeout_ms=50) != PD_ACCEPT:  # джерело має відповісти Accept у межах таймауту
        return False                         # відмова → контракту нема, на шині 5 В
    pd.wait_event(PD_PS_RDY)                  # PS_RDY: нова напруга на VBUS стоїть
    gate_enable()                            # ЛИШЕ ТЕПЕР замкнути ключ на навантаження
    return True                              # контракт діє, 12 В дійшли до пристрою
