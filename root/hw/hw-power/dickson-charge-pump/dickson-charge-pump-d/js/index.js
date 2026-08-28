function main() {
  const Vin   = 3.3;      // напруга живлення, В
  const Vphi  = 3.3;      // розмах такту (гойдається на всю шину), В
  const Vd    = 0.3;      // падіння на одному клапані, В
  const Vgoal = 18.0;     // цільова напруга, В
  const Iout  = 50e-6;    // струм навантаження, А
  const f     = 500e3;    // частота такту, Гц
  const Cs    = 100e-12;  // конденсатор сходинки, Ф

  // Скільки сходинок треба (без урахування провисання):
  // Vgoal = Vin + N*(Vphi - Vd)  →  N = (Vgoal - Vin)/(Vphi - Vd)
  const N_real = (Vgoal - Vin) / (Vphi - Vd);
  const N = Math.ceil(N_real);  // округлюємо вгору — сходинок ціле число
  console.log(`Треба сходинок: ${N_real.toFixed(2)} -> беремо ${N}`);

  // Провисання під навантаженням: Rвих ~ N/(f*Cs)
  const Rout = N / (f * Cs);
  const droop = Iout * Rout;
  console.log(`Вихідний опір: ${Rout.toFixed(0)} Ом, провисання: ${droop.toFixed(2)} В`);

  // Напруга без навантаження і під навантаженням:
  const Voc = Vin + N * (Vphi - Vd);
  const Vload = Voc - droop;
  console.log(`Холостий хід: ${Voc.toFixed(2)} В, під навантаженням: ${Vload.toFixed(2)} В`);
}

main();
