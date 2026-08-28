// Чи лежать аргументи в діапазоні, де дані IPC-2221 виміряні (а не екстрапольовані).
bool ipc2221_in_valid_range(double current_a, double width_mm,
                            double delta_t_c, double copper_oz)
{
    if (current_a > 35.0)                 return false;  // вище — екстраполяція
    if (width_mm  > 400.0 * MM_PER_MIL)   return false;  // 400 мілів ≈ 10.16 мм
    if (delta_t_c < 10.0 || delta_t_c > 100.0) return false;
    if (copper_oz < 0.5 || copper_oz > 3.0)    return false;
    return true;
}
