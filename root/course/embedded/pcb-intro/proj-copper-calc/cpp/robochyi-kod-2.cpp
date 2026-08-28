// Переріз мідної стінки via у кв. мілах (наближення тонкої стінки: pi*d*t).
//   drill_mm  — діаметр отвору (свердла), мм
//   plating_um — товщина металізації (мідної стінки), мкм
// Повертає площу в кв. мілах, або -1.0 при некоректних аргументах.
double via_barrel_area_mils2(double drill_mm, double plating_um)
{
    if (drill_mm <= 0.0 || plating_um <= 0.0)
        return -1.0;                       // безглузді розміри — не вгадуємо

    double drill_mil   = drill_mm / MM_PER_MIL;        // діаметр у мілах
    double plating_mil = (plating_um * 1e-3) / MM_PER_MIL;  // мкм->мм->мил
    return PI_ * drill_mil * plating_mil;  // A ~ периметр * товщина
}
