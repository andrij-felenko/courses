#include <string>
#include <vector>
#include <numeric>

// Пасивні дані — жодної поведінки, лише опис працівника.
struct EmployeeData {
    std::string name;
    double      hourlyRate = 0.0;
    std::vector<double> dailyHours;
};

double totalHours(const EmployeeData& e) {
    return std::accumulate(e.dailyHours.begin(), e.dailyHours.end(), 0.0);
}

// ЯВНА спільна одиниця. Тепер це не прихований хелпер, а названий
// контракт із власником. Хто нею користується — залежить СВІДОМО;
// зміна тут — видима зміна спільного правила, а не тиха правка.
class HoursPolicy {
public:
    explicit HoursPolicy(double regularCap) : cap_(regularCap) {}

    // Скільки годин рахувати звичайними (решта — понаднормові).
    double regularHours(const EmployeeData& e) const {
        double total = totalHours(e);
        return total < cap_ ? total : cap_;
    }
    double overtimeHours(const EmployeeData& e) const {
        return totalHours(e) - regularHours(e);
    }
private:
    double cap_;   // поріг звичайних годин — тепер параметр, не «40» у тілі
};

// CFO: тільки нарахування. Залежить від політики годин ЯВНО.
class PayCalculator {
public:
    explicit PayCalculator(HoursPolicy policy) : policy_(policy) {}

    double calculatePay(const EmployeeData& e) const {
        double reg = policy_.regularHours(e);
        double ot  = policy_.overtimeHours(e);
        return reg * e.hourlyRate + ot * e.hourlyRate * overtimeRate_;
    }
private:
    HoursPolicy policy_;
    double overtimeRate_ = 1.5;   // множник понаднормових — живе ТУТ, у CFO
};

// COO: тільки звіт. Теж залежить від політики годин ЯВНО.
class HourReporter {
public:
    explicit HourReporter(HoursPolicy policy) : policy_(policy) {}

    std::string report(const EmployeeData& e) const {
        double reg = policy_.regularHours(e);
        double ot  = policy_.overtimeHours(e);
        return e.name + ": reg=" + fmt(reg) + " ot=" + fmt(ot);
    }
private:
    HoursPolicy policy_;
    static std::string fmt(double v);
};

// CTO/DBA: тільки збереження. Про години й зарплату не знає нічого.
class EmployeeRepository {
public:
    void save(const EmployeeData& e);   // серіалізація у базу
};
