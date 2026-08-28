// Стеля SNR (дБ) від апертурного джиттера
// fHz   — частота вхідного сигналу, Гц
// tjSec — RMS-джиттер такту, с
function jitterSnrDb(fHz, tjSec) {
    const x = 2.0 * Math.PI * fHz * tjSec;
    return -20.0 * Math.log10(x);
}

// Скільки ефективних розрядів (ENOB) лишає ця стеля
function jitterEnob(fHz, tjSec) {
    const snr = jitterSnrDb(fHz, tjSec);
    return (snr - 1.76) / 6.02;        // SNR ≈ 6.02·ENOB + 1.76
}

// приклад: jitterSnrDb(10e6, 1e-12) ≈ 84.0;  jitterEnob(...) ≈ 13.7
