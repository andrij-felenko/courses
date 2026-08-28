// 1. Перемикання системного джерела SYSCLK на внутрішній HSI
rcc.cfgr = (rcc.cfgr & ~0x03UL) | 0x00UL;
while ((rcc.cfgr & 0x0CUL) != 0x00UL) {
    // Очікування підтвердження комутації
}

// 2. Вимкнення контуру PLL
rcc.cr &= ~(1UL << 24);

// 3. Зменшення затримок Flash-пам'яті до 0 WS
flash.acr = (flash.acr & ~0x07UL) | 0x00UL;
