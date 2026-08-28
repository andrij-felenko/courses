#include <iostream>
#include <vector>
#include <cmath>
#include <string_view>
#include <numeric>
#include <iomanip>

struct TCOOption {
    std::string_view name;
    double initial_cost;
    double quarterly_base_infra;
    double sre_fte_count;
    double sre_quarterly_salary;
    double saas_cost_per_unit;
    double vendor_annual_growth;
    double egress_cost_per_gb;
};

struct TCOResult {
    double total_npv;
    std::vector<double> quarterly_discounted;
};

TCOResult calculate_3year_tco(
    const TCOOption& opt,
    const std::vector<int>& quarterly_units,
    const std::vector<double>& quarterly_egress_gb,
    double annual_discount_rate = 0.08)
{
    double quarterly_r = std::pow(1.0 + annual_discount_rate, 0.25) - 1.0;
    double total_npv = opt.initial_cost;
    std::vector<double> q_costs(12, 0.0);

    for (size_t q = 0; q < 12; ++q) {
        size_t year = q / 4;
        double units = static_cast<double>(quarterly_units[q]);
        double egress = quarterly_egress_gb[q];

        double vendor_markup = std::pow(1.0 + opt.vendor_annual_growth, static_cast<double>(year));
        double license_cost = units * opt.saas_cost_per_unit * vendor_markup;
        double ops_cost = opt.sre_fte_count * opt.sre_quarterly_salary;
        double egress_cost = egress * opt.egress_cost_per_gb;

        double raw_cost = license_cost + ops_cost + opt.quarterly_base_infra + egress_cost;
        double discount_factor = std::pow(1.0 + quarterly_r, static_cast<double>(q + 1));
        double discounted = raw_cost / discount_factor;

        total_npv += discounted;
        q_costs[q] = discounted;
    }

    return {total_npv, std::move(q_costs)};
}

int find_crossover_units(const TCOOption& saas, const TCOOption& self_h) {
    for (int units = 1000; units < 200000; units += 1000) {
        double saas_q = units * saas.saas_cost_per_unit * (1.0 + saas.vendor_annual_growth) +
                        (saas.sre_fte_count * saas.sre_quarterly_salary);
        double self_q = self_h.quarterly_base_infra +
                        (self_h.sre_fte_count * self_h.sre_quarterly_salary);
        if (saas_q > self_q) {
            return units;
        }
    }
    return 200000;
}

int main() {
    std::vector<int> units(12);
    std::vector<double> egress(12);
    for (int i = 0; i < 12; ++i) {
        units[i] = 10000 + i * 8000;
        egress[i] = 5000.0 + i * 2000.0;
    }

    TCOOption saas{"Managed SaaS", 15000.0, 0.0, 0.25, 25000.0, 1.50, 0.15, 0.09};
    TCOOption self_hosted{"Self-Hosted OS", 80000.0, 6000.0, 1.50, 25000.0, 0.0, 0.0, 0.02};

    auto res_saas = calculate_3year_tco(saas, units, egress);
    auto res_self = calculate_3year_tco(self_hosted, units, egress);
    int n_star = find_crossover_units(saas, self_hosted);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "3-Year TCO SaaS: $" << res_saas.total_npv << "\n";
    std::cout << "3-Year TCO Self-Hosted: $" << res_self.total_npv << "\n";
    std::cout << "Crossover N*: " << n_star << " units\n";
    return 0;
}
