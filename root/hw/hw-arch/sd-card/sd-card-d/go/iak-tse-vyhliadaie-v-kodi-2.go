// Прочитати один 512-байтовий сектор у buf (зріз на 512). lba — номер сектора.
// Для SDHC/SDXC адреса = номер сектора; для старих SDSC було б lba*512.
func sdReadBlock(dev *SPI, csHigh, csLow func(), lba uint32, buf []byte) error {
    csLow()
    if sdCmd(dev, 17, lba, 0xFF) != 0x00 {   // CMD17: read single block
        csHigh()
        return errCmd17
    }
    var token byte = 0xFF                     // чекаємо маркер початку даних
    for token == 0xFF {
        token = xchg(dev, 0xFF)
    }
    if token != 0xFE {                        // 0xFE = дані пішли
        csHigh()
        return errBadToken
    }
    for i := 0; i < 512; i++ {                // рівно 512 байтів
        buf[i] = xchg(dev, 0xFF)
    }
    xchg(dev, 0xFF); xchg(dev, 0xFF)          // два байти CRC -> у SPI відкидаємо
    csHigh()
    return nil                                // сектор у buf
}
