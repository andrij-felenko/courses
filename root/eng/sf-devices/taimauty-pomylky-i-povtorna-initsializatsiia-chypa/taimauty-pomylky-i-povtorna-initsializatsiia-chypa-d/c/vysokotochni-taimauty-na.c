void dwt_init(void) {
    // Вмикаємо біт TRCENA (Trace Enable, біт 24) у регістрі DEMCR
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    
    // Скидаємо лічильник циклів у нуль
    DWT->CYCCNT = 0;
    
    // Вмикаємо біт CYCCNTENA (біт 0) у регістрі керування DWT_CTRL
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}
