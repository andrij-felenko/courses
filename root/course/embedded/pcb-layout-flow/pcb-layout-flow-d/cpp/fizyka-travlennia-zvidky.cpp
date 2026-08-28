// Компенсація травлення: наскільки розширити малюнок доріжки,
// щоб ПІСЛЯ ізотропного підтраву вона вийшла цільової ширини.
// Усі величини — у мікрометрах.
struct EtchComp {
    float target_um;   // цільова ширина готової доріжки
    float draw_um;     // ширина, яку слід намалювати (з компенсацією)
    float undercut_um; // підтрав з одного боку
};

EtchComp etch_compensate(float target_um,
                         float copper_thickness_um, // 35 = 1oz, 70 = 2oz
                         float etch_factor)          // типово 2..4
{
    EtchComp r;
    r.target_um    = target_um;
    r.undercut_um  = copper_thickness_um / etch_factor;   // u = t / EF
    // готова = намальована − 2u  ⇒  намальована = цільова + 2u
    r.draw_um      = target_um + 2.0f * r.undercut_um;
    return r;
}

// Приклад: хочемо готову доріжку 150 мкм на міді 1oz, EF=3
//   u        = 35 / 3      ≈ 11.7 мкм
//   малювати = 150 + 23.4  ≈ 173.4 мкм
// Тобто щоб отримати рівні 150 мкм, малюнок має бути ~173 мкм —
// цю поправку завод вносить сам, але тепер зрозуміло ЧОМУ вона є.
