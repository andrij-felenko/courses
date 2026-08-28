# Самодіагностика живлення: пристрій сам ставить діагноз замість користувача.
# vbus_mv — виміряний АЦП VBUS у мілівольтах; i_charge_ma — струм заряду.
from enum import Enum, auto

class PowerDiag(Enum):
    OK          = auto()  # напруга тримається, струм є — усе гаразд
    CABLE_DROP  = auto()  # напруга просіла під струмом — винен кабель/контакт
    NEGOTIATION = auto()  # напруга є, а струму нема — не домовилися
    SOFT_SOURCE = auto()  # і струм, і просадка — м'який блок
    NO_POWER    = auto()  # напруги майже нема — контакт/цілість

VBUS_NOMINAL_MV = 5000
VBUS_SAG_MV     = 4400   # нижче — вважаємо просадкою
VBUS_DEAD_MV    = 3000   # нижче — живлення практично нема
I_EXPECT_MA     = 900    # скільки ми домовилися тягти

def diagnose_power(vbus_mv: int, i_charge_ma: int) -> PowerDiag:
    if vbus_mv < VBUS_DEAD_MV:                       # майже нуль — шукай контакт
        return PowerDiag.NO_POWER

    sag = vbus_mv < VBUS_SAG_MV                       # напруга просіла?
    low_current = i_charge_ma < I_EXPECT_MA // 2      # струм сильно нижчий за очікуваний?

    if sag and not low_current:                      # тягнемо струм, а напруга падає → кабель
        return PowerDiag.CABLE_DROP
    if sag and low_current:                          # і те, і те → м'який блок
        return PowerDiag.SOFT_SOURCE
    if not sag and low_current:                      # напруга є, струму нема → переговори
        return PowerDiag.NEGOTIATION
    return PowerDiag.OK                              # тримається й тягне → усе добре
