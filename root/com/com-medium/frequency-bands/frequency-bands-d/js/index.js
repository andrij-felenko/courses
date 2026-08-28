// Довжина чвертьхвильової антени для частоти каналу.
// c у мм/с, щоб одразу дістати міліметри.
function quarterWaveMm(freqHz) {
    const c = 299792458.0 * 1000.0;   // швидкість світла, мм/с
    const lambdaMm = c / freqHz;      // λ = c / f
    return lambdaMm / 4.0;            // чверть хвилі
}

// 433 МГц → ≈173 мм (17 см);  2.4 ГГц → ≈31 мм (3 см)
const ant433  = quarterWaveMm(433.0e6);
const ant2400 = quarterWaveMm(2400.0e6);
