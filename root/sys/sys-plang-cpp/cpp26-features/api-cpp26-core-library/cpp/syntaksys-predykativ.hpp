// Приклад функції з повною специфікацією контракту
double calculate_log(double x, double base)
    pre (x > 0.0)
    pre (base > 0.0 && base != 1.0)
    post [res] (res == res) // Перевірка відсутності нечислових значень NaN
{
    double val = std::log(x) / std::log(base);
    contract_assert(!std::isnan(val));
    return val;
}
