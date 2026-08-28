// Дві точки калібрування, зняті один раз і збережені:
const int32_t zero_code  = 8200L;     // код порожніх ваг (тара)
const int32_t ref_code   = 412600L;   // код під еталоном
const float   ref_grams  = 1000.0f;   // маса еталона, г

// Масштаб: скільки грамів на один крок коду
//   (412600 − 8200) кроків  ↔  1000 г
const float scale = ref_grams / (float)(ref_code - zero_code);
//   scale = 1000 / 404400 ≈ 0.002473 г/крок

// Перерахунок будь-якого свіжого коду в грами:
float code_to_grams(int32_t raw_code) {
    return (float)(raw_code - zero_code) * scale;
}

// Перевірка: хай прийшов код 210 400
//   (210400 − 8200) · 0.002473 ≈ 202200 · 0.002473 ≈ 500.0 г
