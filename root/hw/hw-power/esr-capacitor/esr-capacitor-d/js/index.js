// Скільки тепла народжує пульсівний струм на ESR конденсатора.
// iRms — діюче значення пульсації, А; esr — еквівалентний послідовний опір, Ом.

function rippleHeat(iRms, esr) {
    return iRms * iRms * esr;       // P = I² · ESR, Вт
}

const i = 2.0;                                             // пульсівний струм 2 А (rms)
console.log(`ESR=0.50: P = ${rippleHeat(i, 0.50).toFixed(2)} W`);  // звичайний електроліт
console.log(`ESR=0.02: P = ${rippleHeat(i, 0.02).toFixed(2)} W`);  // low-ESR
