#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <limits>
#include <sstream>

enum class PlatformStatus {
    PrematureDeficit,
    NoPlatformNeeded,
    TransitionScaffold,
    MatureProfitable
};

std::string status_to_string(PlatformStatus st) {
    switch (st) {
        case PlatformStatus::PrematureDeficit: return "PREMATURE_DEFICIT";
        case PlatformStatus::NoPlatformNeeded: return "NO_PLATFORM_NEEDED";
        case PlatformStatus::TransitionScaffold: return "TRANSITION_SCAFFOLD";
        case PlatformStatus::MatureProfitable: return "MATURE_PROFITABLE";
    }
    return "UNKNOWN";
}

struct AuditInput {
    int num_stream_teams{0};
    int team_size{0};
    double engineer_hourly_rate{0.0};
    double infra_time_ratio{0.0};
    int platform_engineers{0};
    double platform_hourly_rate{0.0};
    double friction_delay_ratio{0.02};
    double platform_efficiency{0.75};
    int annual_hours{1920};
    double discount_rate{0.10};
    double team_growth_rate_annual{0.20};
};

struct NpvProjection {
    int year;
    int num_teams;
    double gross_benefit;
    double platform_cost;
    double net_cash_flow;
    double discounted_cash_flow;
};

struct AuditReport {
    PlatformStatus status;
    double annual_base_infra_cost;
    double annual_platform_team_cost;
    double annual_net_roi;
    double break_even_teams;
    double npv_3year;
    std::vector<NpvProjection> projections;
    std::vector<std::string> recommendations;
};

class PlatformAuditor {
public:
    static AuditReport evaluate(const AuditInput& inp) {
        AuditReport rep;
        
        const int total_stream_engineers = inp.num_stream_teams * inp.team_size;
        const double base_infra_cost_per_hour = total_stream_engineers * inp.engineer_hourly_rate * inp.infra_time_ratio;
        rep.annual_base_infra_cost = base_infra_cost_per_hour * inp.annual_hours;
        
        const double platform_team_cost_per_hour = inp.platform_engineers * inp.platform_hourly_rate;
        rep.annual_platform_team_cost = platform_team_cost_per_hour * inp.annual_hours;
        
        const double eff_saved_ratio = (inp.infra_time_ratio * inp.platform_efficiency) - inp.friction_delay_ratio;
        const double single_team_hourly_savings = inp.team_size * inp.engineer_hourly_rate * eff_saved_ratio;
        
        if (single_team_hourly_savings > 0.0) {
            rep.break_even_teams = platform_team_cost_per_hour / single_team_hourly_savings;
        } else {
            rep.break_even_teams = std::numeric_limits<double>::infinity();
        }
        
        const double net_hourly_benefit = (inp.num_stream_teams * single_team_hourly_savings) - platform_team_cost_per_hour;
        rep.annual_net_roi = net_hourly_benefit * inp.annual_hours;
        
        double npv_total = 0.0;
        double current_teams = static_cast<double>(inp.num_stream_teams);
        
        for (int yr = 1; yr <= 3; ++yr) {
            int n_teams_int = static_cast<int>(std::round(current_teams));
            double gross_b = n_teams_int * single_team_hourly_savings * inp.annual_hours;
            double p_cost = rep.annual_platform_team_cost;
            
            if (n_teams_int > 8 && inp.platform_engineers > 0) {
                int extra_eng = (n_teams_int - 8) / 4;
                p_cost += extra_eng * inp.platform_hourly_rate * inp.annual_hours;
            }
            
            double net_cf = gross_b - p_cost;
            double dcf = net_cf / std::pow(1.0 + inp.discount_rate, yr);
            npv_total += dcf;
            
            rep.projections.push_back(NpvProjection{
                .year = yr,
                .num_teams = n_teams_int,
                .gross_benefit = gross_b,
                .platform_cost = p_cost,
                .net_cash_flow = net_cf,
                .discounted_cash_flow = dcf
            });
            
            current_teams *= (1.0 + inp.team_growth_rate_annual);
        }
        rep.npv_3year = npv_total;
        
        if (single_team_hourly_savings <= 0.0) {
            rep.status = PlatformStatus::PrematureDeficit;
            rep.recommendations.push_back("КРИТИЧНО: Платформа додає більше тертя, ніж заощаджує часу розробників.");
            rep.recommendations.push_back("Спростіть платформу до Thinnest Viable Platform (TVP).");
        } else if (inp.platform_engineers > 0 && inp.num_stream_teams < rep.break_even_teams) {
            rep.status = PlatformStatus::PrematureDeficit;
            rep.recommendations.push_back("ПОПЕРЕДЖЕННЯ: Витрати на платформну команду перевищують вигоди.");
            rep.recommendations.push_back("Переформатуйте команду у режим Enabling Team.");
        } else if (inp.num_stream_teams < 3 && inp.platform_engineers == 0) {
            rep.status = PlatformStatus::NoPlatformNeeded;
            rep.recommendations.push_back("Оптимальний стан: використовуйте ванільні IaC-шаблони без виділеної команди.");
        } else if (inp.num_stream_teams >= 3 && inp.num_stream_teams < 5 && inp.platform_engineers == 0) {
            rep.status = PlatformStatus::TransitionScaffold;
            rep.recommendations.push_back("Перехідна зона: рекомендовано підготувати TVP (1 інженер).");
        } else {
            rep.status = PlatformStatus::MatureProfitable;
            rep.recommendations.push_back("ОПТИМАЛЬНО: Платформа дає високий позитивний економічний ефект.");
        }
        
        return rep;
    }
};

int main() {
    AuditInput input{
        .num_stream_teams = 6,
        .team_size = 5,
        .engineer_hourly_rate = 50.0,
        .infra_time_ratio = 0.30,
        .platform_engineers = 2,
        .platform_hourly_rate = 60.0,
        .friction_delay_ratio = 0.02,
        .platform_efficiency = 0.75
    };
    
    AuditReport report = PlatformAuditor::evaluate(input);
    
    std::cout << "=== Сценарій 2 (Зрілий IDP) ===" << std::endl;
    std::cout << "Статус: " << status_to_string(report.status) << std::endl;
    std::cout << "Річний чистий ROI: $" << std::fixed << std::setprecision(2) << report.annual_net_roi << std::endl;
    std::cout << "Точка окупності: " << report.break_even_teams << " команд" << std::endl;
    std::cout << "3-річний NPV: $" << report.npv_3year << std::endl;
    for (const auto& rec : report.recommendations) {
        std::cout << "  * " << rec << std::endl;
    }
    return 0;
}
