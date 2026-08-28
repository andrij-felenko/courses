// Самодіагностика живлення: пристрій сам ставить діагноз замість користувача.
// vbus_mv — виміряний АЦП VBUS у мілівольтах; i_charge_ma — струм заряду.
typedef enum {
    PWR_OK,            // напруга тримається, струм є — усе гаразд
    PWR_CABLE_DROP,    // напруга просіла під струмом — винен кабель/контакт
    PWR_NEGOTIATION,   // напруга є, а струму нема — не домовилися
    PWR_SOFT_SOURCE,   // і струм, і просадка — м'який блок
    PWR_NO_POWER       // напруги майже нема — контакт/цілість
} power_diag_t;

#define VBUS_NOMINAL_MV   5000
#define VBUS_SAG_MV       4400   // нижче — вважаємо просадкою
#define VBUS_DEAD_MV      3000   // нижче — живлення практично нема
#define I_EXPECT_MA        900   // скільки ми домовилися тягти

power_diag_t diagnose_power(uint16_t vbus_mv, uint16_t i_charge_ma) {
    if (vbus_mv < VBUS_DEAD_MV)               // майже нуль — шукай контакт
        return PWR_NO_POWER;

    bool sag = (vbus_mv < VBUS_SAG_MV);       // напруга просіла?
    bool low_current = (i_charge_ma < I_EXPECT_MA / 2);  // струм сильно нижчий за очікуваний?

    if (sag && !low_current) return PWR_CABLE_DROP;   // тягнемо струм, а напруга падає → кабель
    if (sag &&  low_current) return PWR_SOFT_SOURCE;  // і те, і те → м'який блок
    if (!sag && low_current) return PWR_NEGOTIATION;  // напруга є, струму нема → переговори
    return PWR_OK;                                    // тримається й тягне → усе добре
}
