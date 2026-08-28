// ТОНКИЙ фасад: лише делегує. Сам НІЧОГО не рахує й не вирішує.
// Актора в нього немає — він порожній посередник.
class EmployeeFacade {
public:
    EmployeeFacade(PayCalculator pay, HourReporter rep, EmployeeRepository repo)
        : pay_(pay), rep_(rep), repo_(repo) {}

    double      calculatePay(const EmployeeData& e) const { return pay_.calculatePay(e); }
    std::string reportHours(const EmployeeData& e) const { return rep_.report(e); }
    void        save(EmployeeData& e)                     { repo_.save(e); }

private:
    PayCalculator      pay_;
    HourReporter       rep_;
    EmployeeRepository repo_;
};
