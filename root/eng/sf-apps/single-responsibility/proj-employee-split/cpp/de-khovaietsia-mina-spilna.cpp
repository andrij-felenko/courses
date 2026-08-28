class Employee {
public:
    explicit Employee(EmployeeData d) : data_(std::move(d)) {}

    // CFO: зарплата = звичайні години × ставка
    //             + понаднормові × ставка × 1.5
    double calculatePay() {
        double reg = regularHours();                 // ← спільна арифметика
        double total = totalHours();
        double overtime = total - reg;
        return reg * data_.hourlyRate
             + overtime * data_.hourlyRate * 1.5;
    }

    // COO: рядок звіту — окремо звичайні, окремо понаднормові
    std::string reportHours() {
        double reg = regularHours();                 // ← та сама спільна
        double total = totalHours();
        double overtime = total - reg;
        return data_.name + ": reg=" + fmt(reg)
             + " ot=" + fmt(overtime);
    }

    void save() { /* пише data_ у базу — тут не суттєво */ }

private:
    double totalHours() {
        double s = 0.0;
        for (double h : data_.dailyHours) s += h;
        return s;
    }

    // ПРИХОВАНА СПІЛЬНА ЗАЛЕЖНІСТЬ ДВОХ АКТОРІВ.
    // Скільки годин рахувати як «звичайні» (решта — понаднормові).
    // Політика підприємства: не більше 40 звичайних годин за період.
    double regularHours() {
        double total = totalHours();
        return total < 40.0 ? total : 40.0;
    }

    static std::string fmt(double v);
    EmployeeData data_;
};
