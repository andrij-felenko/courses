# power_diag.py — польовий діагност живлення USB для прошивки.
# MicroPython/CPython: без динаміки в гарячому шляху, фіксований стан.
from enum import IntEnum
from dataclasses import dataclass

# Діагноз стану живлення — п'ять клітинок матриці напруга×струм.
class PwrDiag(IntEnum):
    OK          = 0   # напруга тримається, струм є — усе гаразд
    CABLE_DROP  = 1   # напруга просіла ПІД струмом — кабель/контакт
    NEGOTIATION = 2   # напруга є, а струму нема — не домовилися (лінії/профіль)
    SOFT_SOURCE = 3   # і просадка, і кволий струм — м'який блок
    NO_POWER    = 4   # напруги майже нема — контакт/цілість кабелю

# Незмінна конфігурація — заповнюється раз під конкретний виріб.
@dataclass(frozen=True)
class PwrCfg:
    vbus_nominal_mv:   int   # очікувана напруга контракту (напр. 5000)
    vbus_sag_mv:       int   # нижче цього вважаємо ПРОСАДКОЮ (напр. 4400)
    vbus_dead_mv:      int   # нижче цього — живлення практично нема (напр. 3000)
    i_expect_ma:       int   # скільки струму ми домовилися тягти
    i_load_min_ma:     int   # менший струм — це «холостий хід», НЕ міряти
    brownout_trip_mv:  int   # нижче — стишуємось (напр. 4000)
    brownout_clear_mv: int   # вище — вертаємось у повний режим (напр. 4300)
    adc_avg_log2:      int   # усереднення: беремо 2^adc_avg_log2 відліків
    debounce_cycles:   int   # діагноз має вистоятися стільки циклів

# Робочий стан — початкові значення означають безпечний холодний старт.
# API об'єкта: step() — один цикл нагляду; low_power/message — читання стану.
class PwrDiagCtx:
    def __init__(self, cfg: PwrCfg):
        self.cfg          = cfg              # конфіг (незмінний, спільний)
        self.diag         = PwrDiag.OK       # ПРИЙНЯТИЙ (стабільний) діагноз
        self.pending      = PwrDiag.OK       # діагноз-кандидат, що ще дебаунситься
        self.pending_run  = 0                # скільки циклів кандидат тримається поспіль
        self.low_power    = False            # режим стишення (гістерезис brownout)
        self.vbus_mv      = cfg.vbus_nominal_mv  # останнє усереднене VBUS (для лога/UI)
        self.i_charge_ma  = 0                # остання оцінка струму
        self.valid        = False            # чи був хоч один вимір під навантаженням
