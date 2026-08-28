// Кожен davach_*() читає регістр стану давача через I2C/SPI,
// обробляє подію й СКИДАЄ прапорець у самому давачі —
// тільки після цього той відпускає лінію IRQ.

#define IRQ_PIN  2   // ніжка МК, куди зведено спільну лінію (активна в 0)

void obrobnyk_irq(void) {
    // Поки лінію хтось тримає внизу — на ній ще є непочате прохання.
    while (digitalRead(IRQ_PIN) == 0) {
        // Порядок опитування = пріоритет джерел.
        if (davach_ruhu_prosyt())   obsluhy_ruh();      // найважливіший
        else if (godynnyk_prosyt()) obsluhy_godynnyk();
        else if (knopka_prosyt())   obsluhy_knopku();
        else break;   // ніхто не зізнається — уникаємо вічного циклу
    }
}
