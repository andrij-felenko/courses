namespace brownian {

enum class SimMode {
    ExactLangevin = 0, // Повне рівняння Ланжевена
    Overdamped     = 1, // Перевизначений режим без інерції
    Rotational     = 2, // Обертальна дифузія
    ActiveSwimmer  = 3  // Активний мікроплавець
};

} // namespace brownian
