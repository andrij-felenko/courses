# power_monitor.py — монітор захищеної шини живлення:
#   вимір напруги дільником+АЦП, гістерезис, класифікація аварії, реакція.
#   Той самий фіксований буфер і жодних блокувань — придатне і для MicroPython.
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Callable, Optional

# Клас стану входу живлення — саме те, заради чого монітор існує.
class PmClass(IntEnum):
    OK        = 0     # шина в нормі, живлення дійшло
    SAG       = 1     # просад: живлення є, але нижче норми (слабке джерело/кабель)
    DEAD      = 2     # мертва шина: ≈0 В (обрив або згорілий запобіжник)
    BODYDIODE = 3     # струм крізь body-діод: FET недовідкрився (реверс/низький Vin)

# Незмінна конфігурація — заповнюється раз під конкретну плату (frozen = const).
@dataclass(frozen=True)
class PmConfig:
    div_num: int; div_den: int       # коефіцієнт дільника: Vшини = Vадц * num/den
    vref_mv: int                     # опора АЦП у мВ (повна шкала)
    adc_full: int                    # максимальний код АЦП (напр. 4095 для 12 біт)

    v_nominal_mv: int                # очікувана напруга шини в нормі, мВ
    v_dead_mv: int                   # нижче цього шина вважається мертвою
    v_sag_trip_mv: int               # нижче цього — просад (спрацювання)
    v_sag_heal_mv: int               # вище цього — просад знято (відпускання) > trip
    diode_drop_mv: int               # падіння body-діода (для розпізнавання, ~600 мВ)
    diode_tol_mv: int                # допуск навколо «Vвх − diode_drop»

    confirm_dead: int                # скільки поганих поспіль → DEAD (мало)
    confirm_sag: int                 # скільки поганих поспіль → SAG (більше)
    confirm_ok: int                  # скільки добрих поспіль → назад у OK (велике)

# Робочий стан — значення за замовчуванням означають «холодний, ще не міряли».
@dataclass
class PmChannel:
    cfg: PmConfig
    st: PmClass = PmClass.OK           # поточний клас
    bus_mv: int = 0                    # останнє усереднене значення шини, мВ
    _sum: int = 0                      # біжуча сума кільцевого буфера
    _buf: list = field(default_factory=lambda: [0] * 8)  # буфер сирих кодів АЦП
    _head: int = 0                     # курсор буфера
    _count: int = 0                    # наповнення буфера
    bad_run: int = 0                   # поганих поспіль (для гістерезису)
    good_run: int = 0                  # добрих поспіль (для гістерезису)
    flag_latched: bool = False         # «була аварія» — липкий прапорець для сервісу

# Функція вимірювання: read_adc() -> int повертає сирий код АЦП шини.
# Так модуль не прив'язаний до конкретного АЦП (STM32, ESP32, будь-що).
ReadAdc = Callable[[], int]

# Реакції-callback: монітор кличе їх у МОМЕНТ переходу, з контексту poll().
@dataclass
class PmActions:
    save_state: Optional[Callable[[], None]] = None   # зберегти критичне у NVM
    set_load: Optional[Callable[[bool], None]] = None # зняти/подати навантаження (ключ)
    on_class: Optional[Callable[[PmClass], None]] = None  # новий клас (індикація/лог)

# Публічні pm_init / pm_poll / pm_class / pm_bus_mv / pm_fault_latched — нижче.
