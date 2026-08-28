// Дві РІЗНІ політики — бо це дві різні причини для зміни.
// Оплатний поріг міняє трудовий договір (CFO); звітний — аудит (COO).
class PayCalculator {
public:
    PayCalculator(double regularCap, double overtimeRate)
        : cap_(regularCap), overtimeRate_(overtimeRate) {}

    double calculatePay(const EmployeeData& e) const {
        double reg = std::min(totalHours(e), cap_);
        double ot  = totalHours(e) - reg;
        return reg * e.hourlyRate + ot * e.hourlyRate * overtimeRate_;
    }
private:
    double cap_;          // 40 — оплатний поріг, власність CFO
    double overtimeRate_; // 1.5
};

class HourReporter {
public:
    explicit HourReporter(double reportingCap) : cap_(reportingCap) {}

    std::string report(const EmployeeData& e) const {
        double reg = std::min(totalHours(e), cap_);
        double ot  = totalHours(e) - reg;
        return e.name + ": reg=" + fmt(reg) + " ot=" + fmt(ot);
    }
private:
    double cap_;          // 44 — звітний поріг, власність COO
    static std::string fmt(double v);
};
