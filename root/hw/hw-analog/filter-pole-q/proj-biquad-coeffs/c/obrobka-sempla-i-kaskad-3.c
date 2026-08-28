// Опис однієї ланки в рецепті родини: множник частоти і добротність.
typedef struct { float fmul; float Q; } stage_spec;

// Баттерворт 4-го порядку: дві ланки, нижчий Q першим (див. далі — це не випадково).
static const stage_spec BUTTERWORTH_4[] = {
    { 1.0f, 0.5412f },     // ланка 1 — низькодобротна
    { 1.0f, 1.3066f },     // ланка 2 — високодобротна
};

// Зібрати каскад ФНЧ заданої родини під частоту зрізу fc.
// specs[] — рецепт (fmul, Q) на ланку; bq[] — масив під n ланок.
static void build_lowpass(biquad bq[], const stage_spec specs[],
                          uint8_t n, float fc, float fs)
{
    for (uint8_t i = 0; i < n; i++) {
        biquad_lowpass(&bq[i], fc * specs[i].fmul, specs[i].Q, fs);
        biquad_reset(&bq[i]);
    }
}
