// Перевірка отвору: чи майданчик тримає кільце й чи затече мідь у діру.
// Розміри — у міліметрах. Числа-допуски — типові для дешевого процесу.
struct DrillCheck {
    bool ring_ok;         // майданчик достатній для кільця
    bool aspect_ok;       // мідь надійно осяде в отворі
    float ring_nominal;   // фактичне номінальне кільце
    float aspect;         // співвідношення сторін
};

DrillCheck check_hole(float pad_d, float hole_d, float board_thickness,
                     float ring_min = 0.15f,   // гарантоване кільце
                     float misreg   = 0.05f,   // похибка суміщення
                     float d_tol    = 0.05f,   // розкид діаметра
                     float ar_limit = 10.0f)   // межа aspect ratio
{
    DrillCheck c;
    c.ring_nominal = (pad_d - hole_d) * 0.5f;
    // потрібне номінальне кільце з урахуванням найгіршого зсуву й розкиду
    float ring_needed = ring_min + misreg + d_tol * 0.5f;
    c.ring_ok  = c.ring_nominal >= ring_needed;
    c.aspect   = board_thickness / hole_d;
    c.aspect_ok = c.aspect <= ar_limit;
    return c;
}

// via 0.3мм у майданчику 0.6мм на платі 1.6мм:
//   ring_nominal = (0.6 - 0.3)/2 = 0.15 мм
//   ring_needed  = 0.15 + 0.05 + 0.025 = 0.225 мм  → 0.15 < 0.225 → ЗАМАЛИЙ!
//   aspect       = 1.6 / 0.3 = 5.3 ≤ 10 → ок
// Мораль: «майданчик удвічі більший за отвір» ЗАМАЛО з урахуванням суміщення.
// Треба 0.75 мм, не 0.6. Саме цю помилку EDA-DRC і ловить.
