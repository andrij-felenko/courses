static bool configure_m8(void) {
    // CFG-RATE: measRate(мс, LE) · navRate · timeRef. 100 мс = 10 Гц.
    uint8_t rate[6] = { 100, 0,   // measRate = 100 (0x0064) LE
                        1,   0,   // navRate  = 1
                        1,   0 }; // timeRef  = 1 (GPS)
    if (!ubx_send_await(UBX_CLS_CFG, UBX_CFG_RATE, rate, sizeof rate, 300, 2))
        return false;

    // CFG-MSG: увімкнути NAV-PVT на поточному порту (rate=1).
    uint8_t msg[3] = { UBX_CLS_NAV, UBX_NAV_PVT, 1 };
    if (!ubx_send_await(UBX_CLS_CFG, UBX_CFG_MSG, msg, sizeof msg, 300, 2))
        return false;

    // ... аналогічно: вимкнути NMEA-речення (CFG-MSG rate=0 для кожного),
    //     CFG-GNSS для сузір'їв, CFG-PRT для швидкості (останнім, з переходом),
    //     CFG-CFG для збереження у Flash.
    return true;
}
