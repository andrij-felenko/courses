// load — інтерфейс до електронного навантаження (CC);
// in_  — вимір ВХОДУ перетворювача (друге джерело даних).
// Крокуємо струм від 0.5 до 4.0 А по 0.5 А і друкуємо ККД.
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (let iset = 0.5; iset <= 4.0 + 1e-3; iset += 0.5) {
    await load.setCurrent(iset);   // уставка струму CC: контур притисне MOSFET
    await sleep(200);              // даємо джерелу й контуру усталитися

    const vout = await load.readVoltage();   // напруга на клемах джерела
    const iact = await load.readCurrent();   // реальний струм (≈ iset)
    const pout = vout * iact;                // вихідна потужність

    const pin = in_.voltage() * in_.current();   // вхідна потужність
    const eff = pin > 0.0 ? pout / pin : 0.0;

    console.log(
        `I=${iact.toFixed(2)} A  Vout=${vout.toFixed(3)} V  ` +
        `Pout=${pout.toFixed(2)} W  eff=${(eff * 100.0).toFixed(1)} %`
    );
}
await load.setCurrent(0.0);        // прибрати навантаження наприкінці
