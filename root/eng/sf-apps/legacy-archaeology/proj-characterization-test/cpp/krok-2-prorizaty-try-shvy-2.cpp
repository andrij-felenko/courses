// Легасі-клас: десь глибоко в processDay() сам бере "зараз".
class BillingRun {
public:
    int processDay(double net, const std::string& country) {
        std::tm today = currentDate();          // <-- приховане звернення
        int days = daysUntilMonthEnd(today);
        // ... купа логіки, що спирається на days ...
        return days * 2;                        // умовний "результат"
    }
protected:
    // ШОВ: єдина точка, де клас дізнається дату. Робимо її virtual,
    // щоб у тесті перекрити — не чіпаючи ні краплі processDay().
    virtual std::tm currentDate() {
        std::time_t t = std::time(nullptr);
        return *std::localtime(&t);
    }
private:
    static int daysUntilMonthEnd(const std::tm& d);
};

// У тесті: успадковуємось і підміняємо ЛИШЕ дату. Уся інша логіка —
// справжня, недоторкана. Це і є "subclass and override".
class BillingRunAt : public BillingRun {
public:
    explicit BillingRunAt(std::tm fixed) : fixed_(fixed) {}
protected:
    std::tm currentDate() override { return fixed_; }
private:
    std::tm fixed_;
};
