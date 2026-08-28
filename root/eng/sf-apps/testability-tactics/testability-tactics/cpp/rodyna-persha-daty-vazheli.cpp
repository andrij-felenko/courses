// Джерела стали параметрами через інтерфейси — тест підставить свої.
struct RateSource { virtual double rate() = 0; };
struct Clock      { virtual bool is_weekend() = 0; };

double order_total(const Order& o, RateSource& rates, Clock& clock) {
    double sum = o.amount * rates.rate();
    if (clock.is_weekend())
        sum *= 1.05;
    return sum;
}
