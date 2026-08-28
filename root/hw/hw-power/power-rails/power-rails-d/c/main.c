// Підняти рейки строго по черзі: ядро → вв/в → периферія
bool power_up_sequence(void) {
    rail_enable(RAIL_CORE_1V8);                 // 1) ядро першим
    if (!wait_rail_good(RAIL_CORE_1V8, 5))      // чекаємо «good» до 5 мс
        return false;                           // не піднялось — стоп, не йдемо далі

    rail_enable(RAIL_IO_3V3);                   // 2) входи-виходи
    if (!wait_rail_good(RAIL_IO_3V3, 5))
        return false;

    rail_enable(RAIL_PERIPH_5V);                // 3) периферія останньою
    return wait_rail_good(RAIL_PERIPH_5V, 5);
}
