from enum import Enum

class PwrState(Enum):
    OK      = 0
    SAG     = 1
    RECOVER = 2

pwr_state   = PwrState.OK
recover_cnt = 0     # скільки поспіль добрих замірів у RECOVER

# Викликати періодично (напр. з таймера раз на 5 мс) зі свіжим кодом VREFINT.
# Уся логіка порогів + гістерезис зібрана тут.
def pwr_monitor_step(vref_raw):
    global pwr_state, recover_cnt
    vdd = read_vdd_mv(vref_raw)

    if pwr_state is PwrState.OK:
        if vdd < V_SAG_MV:                  # провалилось нижче нижнього порога
            pwr_state = PwrState.SAG        # → важкі дії заборонені

    elif pwr_state is PwrState.SAG:
        if vdd > V_OK_MV:                   # піднялось вище ВЕРХНЬОГО порога
            pwr_state = PwrState.RECOVER    # → карантин, ще не довіряємо
            recover_cnt = 0

    elif pwr_state is PwrState.RECOVER:
        if vdd < V_SAG_MV:                  # знову провалилось, поки чекали
            pwr_state = PwrState.SAG        # → назад у SAG, лічильник скинути
        else:
            recover_cnt += 1
            if recover_cnt >= RECOVER_HOLD:
                pwr_state = PwrState.OK     # протрималось стабільно → повна довіра

# Єдине вікно у світ для решти прошивки: чи безпечні зараз важкі дії?
def pwr_heavy_ok():
    return pwr_state is PwrState.OK
