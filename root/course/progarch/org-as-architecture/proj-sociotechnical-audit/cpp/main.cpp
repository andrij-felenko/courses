// Утиліта аналізу соціотехнічного незбігу мовою C++20 (RAII, std::string_view, std::expected)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <array>
#include <numeric>
#include <algorithm>
#include <expected>

struct FileTeamMetric {
    std::unordered_map<std::string, std::size_t> team_changes{};
    std::unordered_set<std::string> distinct_teams{};

    [[nodiscard]] std::size_t total_changes() const noexcept {
        std::size_t total = 0;
        for (const auto& [team, count] : team_changes) {
            total += count;
        }
        return total;
    }

    [[nodiscard]] std::pair<std::string_view, double> primary_owner() const noexcept {
        if (team_changes.empty()) return {"Unknown", 0.0};
        
        auto max_it = std::max_element(team_changes.begin(), team_changes.end(),
            [](const auto& a, const auto& b) { return a.second < b.second; });
        
        const double total = static_cast<double>(total_changes());
        const double tor = total > 0.0 ? static_cast<double>(max_it->second) / total : 0.0;
        return {max_it->first, tor};
    }
};

class SociotechnicalAuditor {
public:
    using TeamMap = std::unordered_map<std::string, std::string>;

    explicit SociotechnicalAuditor(TeamMap team_mapping) 
        : team_map_(std::move(team_mapping)) {}

    [[nodiscard]] std::expected<void, std::string> run_audit_stream(FILE* pipe) {
        if (!pipe) {
            return std::unexpected("Некоректний дескриптор потоку git log");
        }

        std::array<char, 1024> buffer{};
        std::string current_team = "Unknown";

        while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe)) {
            std::string_view line(buffer.data());
            if (line.back() == '\n') line.remove_suffix(1);
            if (line.back() == '\r') line.remove_suffix(1);
            if (line.empty()) continue;

            if (line.starts_with("COMMIT|")) {
                auto email = line.substr(7);
                auto it = team_map_.find(std::string(email));
                current_team = (it != team_map_.end()) ? it->second : "ExternalTeam";
            } else {
                parse_numstat_line(line, current_team);
            }
        }
        return {};
    }

    void print_report() const {
        std::cout << "=== СОЦІОТЕХНІЧНИЙ АУДИТ КОДОВОЇ БАЗИ (C++20) ===\n";
        std::size_t total_files = metrics_.size();
        std::size_t mismatched_files = 0;

        for (const auto& [filepath, metric] : metrics_) {
            if (metric.distinct_teams.size() > 1) {
                mismatched_files++;
            }
            auto [owner, tor] = metric.primary_owner();
            if (tor < 0.60 && metric.distinct_teams.size() > 1) {
                std::cout << "[УВАГА: НИЗЬКИЙ TOR] " << filepath 
                          << " | Головний власник: " << owner 
                          << " (" << (tor * 100.0) << "%)\n";
            }
        }

        const double cmi = total_files > 0 ? static_cast<double>(mismatched_files) / static_cast<double>(total_files) : 0.0;
        std::cout << "\nЗагалом файлів: " << total_files << "\n";
        std::cout << "Індекс соціотехнічного незбігу (CMI): " << (cmi * 100.0) << "%\n";
    }

private:
    void parse_numstat_line(std::string_view line, std::string_view current_team) {
        auto tab1 = line.find('\t');
        auto tab2 = line.find('\t', tab1 + 1);
        if (tab1 != std::string_view::npos && tab2 != std::string_view::npos) {
            auto added_str = line.substr(0, tab1);
            auto deleted_str = line.substr(tab1 + 1, tab2 - (tab1 + 1));
            auto path = line.substr(tab2 + 1);

            if (added_str != "-" && deleted_str != "-") {
                std::size_t changes = std::stoul(std::string(added_str)) + std::stoul(std::string(deleted_str));
                auto& metric = metrics_[std::string(path)];
                metric.team_changes[std::string(current_team)] += changes;
                metric.distinct_teams.insert(std::string(current_team));
            }
        }
    }

    TeamMap team_map_;
    std::unordered_map<std::string, FileTeamMetric> metrics_{};
};

int main() {
    SociotechnicalAuditor::TeamMap team_map{
        {"dev1@dh.org", "TwinTeam"},
        {"dev2@dh.org", "AutomationTeam"}
    };

    SociotechnicalAuditor auditor(std::move(team_map));
    
    // RAII для автоматичного закриття popen
    struct PipeCloser {
        void operator()(FILE* p) const { if (p) pclose(p); }
    };
    std::unique_ptr<FILE, PipeCloser> pipe(popen("git log --numstat --no-merges --format=COMMIT|%ae", "r"));

    if (auto res = auditor.run_audit_stream(pipe.get()); !res) {
        std::cerr << "Помилка аудиту: " << res.error() << '\n';
        return 1;
    }

    auditor.print_report();
    return 0;
}
