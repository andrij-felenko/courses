void calculate_square_root(double val, std::promise<double> p) {
    try {
        if (val < 0.0) {
            throw std::invalid_argument("Число не може бути від'ємним!");
        }
        p.set_value(std::sqrt(val));
    } catch (...) {
        // Гарантована передача поточного винятку разом зі стеком
        p.set_exception(std::current_exception());
    }
}
