from enum import Enum

class PowerState(Enum):
    RUN = 0
    SAVING = 1
    SLEEP = 2

# Пороги в мілівольтах (для випадку «контролер живиться прямо від Li-ion»).
V_WARN_MV   = 3400   # нижче — тривога (починаємо згортатися)
V_CRIT_MV   = 3150   # нижче — критично (останній флаш і сон)
V_RESUME_MV = 3550   # вище — назад у норму (гістерезис проти торохтіння)
CONFIRM_N   = 3      # стільки вимірів поспіль має підтвердити падіння

state = PowerState.RUN
low_count = 0        # лічильник підтвердження «стало низько»

def power_fsm_tick():
    global state, low_count
    v = read_vcc_filtered_mv()   # згладжений вимір, мВ

    if state is PowerState.RUN:
        if v < V_WARN_MV:
            low_count += 1
            if low_count >= CONFIRM_N:   # не сплеск, а стале падіння
                begin_graceful_save()    # почати згортання (див. нижче)
                state = PowerState.SAVING
                low_count = 0
        else:
            low_count = 0                 # напруга ще здорова — скидаємо лічильник

    elif state is PowerState.SAVING:
        if v < V_CRIT_MV:
            final_flush_and_park()        # останній обов'язковий флаш
            enter_deep_sleep()            # або вимкнення живлення
            state = PowerState.SLEEP
        elif v > V_RESUME_MV:
            resume_normal_operation()     # батарея відновилась (напр., підзарядка)
            state = PowerState.RUN
        # між V_CRIT і V_RESUME лишаємось у SAVING — та сама «мертва зона»

    elif state is PowerState.SLEEP:
        # Прокидаємось лише за зовнішньою подією (підзарядка/скид).
        if v > V_RESUME_MV:
            resume_normal_operation()
            state = PowerState.RUN
