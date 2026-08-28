#include <string>
#include <vector>

// Пасивні дані — те, що описує працівника.
struct EmployeeData {
    std::string name;
    double      hourlyRate = 0.0;   // ставка за звичайну годину
    std::vector<double> dailyHours; // відпрацьовано щодня за період
};

// «Очевидний» God-клас: усе про працівника — тут.
class Employee {
public:
    explicit Employee(EmployeeData d) : data_(std::move(d)) {}

    double calculatePay();   // CFO: правила нарахування
    std::string reportHours(); // COO: формат звіту
    void   save();           // CTO/DBA: як лягає в базу

private:
    EmployeeData data_;
};
