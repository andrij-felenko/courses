// SPI-режим SD. dev — драйвер SPI; csHigh/csLow керують лінією вибору картки.
// xchg обмінює один байт: віддає b, повертає відповідь.
func xchg(dev *SPI, b byte) byte {
    rx := make([]byte, 1)
    dev.Tx([]byte{b}, rx)             // один байт туди й назад
    return rx[0]
}

func sdCmd(dev *SPI, cmd byte, arg uint32, crc byte) byte {
    xchg(dev, 0xFF)                   // такт «вхолосту» перед командою
    xchg(dev, 0x40|cmd)              // стартові біти + номер команди
    xchg(dev, byte(arg>>24)); xchg(dev, byte(arg>>16))
    xchg(dev, byte(arg>>8));  xchg(dev, byte(arg)) // 4 байти, старший першим
    xchg(dev, crc|0x01)             // CRC потрібен лише для CMD0/CMD8
    for i := 0; i < 8; i++ {        // відповідь приходить за кілька тактів
        r := xchg(dev, 0xFF)
        if r&0x80 == 0 {            // старший біт 0 -> це валідна R1
            return r
        }
    }
    return 0xFF                     // картка не відповіла
}

// Розбудити картку й перевести її в SPI-режим. Повертає nil, якщо вдалося.
func sdInit(dev *SPI, csHigh, csLow func()) error {
    dev.SetClock(200_000)            // 100-400 кГц на час ініціалізації
    csHigh()
    for i := 0; i < 10; i++ {        // >= 74 тактів, CS високий
        xchg(dev, 0xFF)
    }

    csLow()
    if sdCmd(dev, 0, 0x00000000, 0x94) != 0x01 { // CMD0: idle
        csHigh()
        return errNoIdle
    }
    sdCmd(dev, 8, 0x000001AA, 0x86)  // CMD8: перевірка діапазону живлення (+ 4 байти R7)
    for i := 0; i < 4; i++ {
        xchg(dev, 0xFF)
    }

    for tries := 0; tries < 1000; tries++ { // ACMD41 у циклі — чекаємо готовності
        sdCmd(dev, 55, 0, 0xFF)      // ACMD = CMD55, потім сама команда
        if sdCmd(dev, 41, 0x40000000, 0xFF) == 0x00 { // біт HCS=1 (підтримка SDHC)
            csHigh()
            dev.SetClock(25_000_000) // готово -> можна на повну частоту
            return nil
        }
    }
    csHigh()
    return errNoIdle                 // картка так і не вийшла з idle
}
