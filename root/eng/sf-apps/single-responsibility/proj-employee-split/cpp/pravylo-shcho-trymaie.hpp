// Податок — у PayCalculator (це нарахування, актор CFO):
double PayCalculator::netPay(const EmployeeData& e) const {
    double gross = calculatePay(e);
    return gross - gross * taxRate_;   // taxRate_ — поле PayCalculator
}

// Верстка відомості — у HourReporter (це подання, актор COO):
std::string HourReporter::payslipLine(const EmployeeData& e,
                                      double gross, double net) const {
    return report(e) + " | gross=" + fmt(gross) + " net=" + fmt(net);
}

// Фасад лишається ТОНКИМ — тільки зводить готове докупи:
std::string EmployeeFacade::payslip(const EmployeeData& e) const {
    double gross = pay_.calculatePay(e);
    double net   = pay_.netPay(e);            // рахунок — у CFO-класі
    return rep_.payslipLine(e, gross, net);   // верстка — у COO-класі
}
