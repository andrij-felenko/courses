// Квадратичний закон у насиченні: Id = 0.5 * k * (Vgs - Vth)^2

function idSat(vgs, vth, k) {
    const vov = vgs - vth;          // перевищення порогу
    if (vov <= 0) return 0;         // нижче порога — канал закрито
    return 0.5 * k * vov * vov;     // квадрат перевищення
}

const vth = 1.0, k = 0.5;
for (const vgs of [1.5, 2.0, 3.0]) {
    const vov = vgs - vth;
    console.log(
        `Vgs=${vgs.toFixed(1)} V  Vov=${vov.toFixed(1)} V  Id=${idSat(vgs, vth, k).toFixed(3)} A`);
}
