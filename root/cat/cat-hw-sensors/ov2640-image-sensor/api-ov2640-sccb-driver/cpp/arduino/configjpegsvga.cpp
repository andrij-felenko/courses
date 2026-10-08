bool configJpegSvga(OV2640Driver& driver) {
    if (!driver.setBank(OV2640Driver::Bank::DSP)) {
        return false;
    }
    
    // Увімкнення JPEG-форматування та оптимізація виходу
    bool success = true;
    success &= driver.writeRegister(OV2640Driver::Bank::DSP, 0xDA, 0x10); // Image mode: JPEG
    success &= driver.writeRegister(OV2640Driver::Bank::DSP, 0xD7, 0x03); // Format select
    
    // Налаштування фактора якості стиснення QS
    success &= driver.writeRegister(OV2640Driver::Bank::DSP, 0x44, 0x0C); // Quality factor
    
    // Задання вихідних розмірів кадру (SVGA 800x600)
    success &= driver.writeRegister(OV2640Driver::Bank::DSP, 0xE1, 0x67); 
    success &= driver.writeRegister(OV2640Driver::Bank::DSP, 0xE2, 0x4B); 
    
    return success;
}
