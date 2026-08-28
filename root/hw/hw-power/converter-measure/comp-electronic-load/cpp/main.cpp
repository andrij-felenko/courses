// load — інтерфейс до електронного навантаження (CC);
// in   — вимір ВХОДУ перетворювача (друге джерело даних).
// Крокуємо струм від 0.5 до 4.0 А по 0.5 А і друкуємо ККД.
for (float iset = 0.5f; iset <= 4.0f + 1e-3f; iset += 0.5f) {
    load.setCurrent(iset);     // уставка струму CC: контур притисне MOSFET
    delay_ms(200);             // даємо джерелу й контуру усталитися

    float vout = load.readVoltage();   // напруга на клемах джерела
    float iact = load.readCurrent();   // реальний струм (≈ iset)
    float pout = vout * iact;          // вихідна потужність

    float pin  = in.voltage() * in.current();   // вхідна потужність
    float eff  = (pin > 0.0f) ? pout / pin : 0.0f;

    printf("I=%.2f A  Vout=%.3f V  Pout=%.2f W  eff=%.1f %%\n",
           iact, vout, pout, eff * 100.0f);
}
load.setCurrent(0.0f);         // прибрати навантаження наприкінці
