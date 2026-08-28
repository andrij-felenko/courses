void setup() {
    // піни під ШІМ: 12 біт — той самий діапазон, що й фаза/гамма
    ledcAttach(2, 5000, 12);
    ledcAttach(4, 5000, 12);
    buildLUT();            // гамма — з конвеєра яскравості
    buildShapeTables();    // форми — один раз

    // приклад: канал 2 одразу дихає, канал 4 чекає на сценарій тривоги
    animStart(2, ANIM_PINGPONG, shapeBreathe, 4000, false);
    queueStart(0, /*pin=*/4, /*invert=*/false, alarmThenCalm, 2);
}

void loop() {
    uint32_t now = millis();
    animTick(now);     // посунути всі ефекти
    queueTick();       // просунути всі черги
    // ↓ цикл вільний: кнопки, зв'язок, давачі — усе живе тут, нічого не блоковано
}
