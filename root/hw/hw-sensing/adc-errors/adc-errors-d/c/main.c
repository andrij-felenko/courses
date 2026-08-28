// дві відомі точки, зняті при калібруванні (відома напруга → код АЦП)
const float V_LO = 0.500f;   int CODE_LO =  600;   // мав би бути ≈ 620 — є зсув і масштаб
const float V_HI = 2.500f;   int CODE_HI = 3000;

// код → напруга по прямій, що проходить через обидві точки
float adc_to_volts(int code) {
    return V_LO + (V_HI - V_LO) * (code - CODE_LO) / (float)(CODE_HI - CODE_LO);
}

// перевірка: рівно посередині між точками маємо вийти на 1.500 В
float v = adc_to_volts(1800);   // = 0.500 + 2.000 × 1200 / 2400 = 1.500 В
