// Струм (А), який пропускає ОДИН via заданого розміру при перегріві dT.
//   drill_mm, plating_um — геометрія отвору
//   delta_t_c            — допустимий перегрів, °C
//   external             — true: рахувати із зовнішнім k (оптимістично);
//                          false: внутрішній k (обережно, за замовчуванням)
// Повертає струм на via в амперах, або -1.0 при некоректних аргументах.
double via_current_a(double drill_mm, double plating_um,
                     double delta_t_c, bool external)
{
    if (delta_t_c <= 0.0) return -1.0;
    double area = via_barrel_area_mils2(drill_mm, plating_um);
    if (area < 0.0) return -1.0;           // прокинути помилку розмірів

    double k = external ? IPC_K_EXTERNAL : IPC_K_INTERNAL;
    return ipc2221_current(area, delta_t_c, k);
}
