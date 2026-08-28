#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <array>

enum class Category {
    Breaking = 0,
    Security,
    Feature,
    Fix,
    Ignore,
    Count
};

struct CommitRecord {
    std::string type;
    std::string scope;
    std::string description;
    std::string cve;
    bool is_breaking{false};
    Category category{Category::Ignore};
};

static std::string_view trim(std::string_view s) {
    const auto start = s.find_first_not_of(" \t\n\r");
    if (start == std::string_view::npos) return {};
    const auto end = s.find_last_not_of(" \t\n\r");
    return s.substr(start, end - start + 1);
}

class ReleaseNotesGenerator {
public:
    static CommitRecord parse_commit(std::string_view raw) {
        CommitRecord rec;

        // Пошук ідентифікатора CVE
        if (const auto cve_pos = raw.find("CVE-"); cve_pos != std::string_view::npos) {
            const auto end_pos = raw.find_first_of(" \t\n\r)]", cve_pos);
            rec.cve = std::string(raw.substr(cve_pos, end_pos - cve_pos));
        }

        if (raw.find("BREAKING CHANGE:") != std::string_view::npos) {
            rec.is_breaking = true;
        }

        const auto colon_pos = raw.find(':');
        if (colon_pos == std::string_view::npos) {
            return rec;
        }

        const auto header = trim(raw.substr(0, colon_pos));
        rec.description = std::string(trim(raw.substr(colon_pos + 1)));

        if (header.find('!') != std::string_view::npos) {
            rec.is_breaking = true;
        }

        const auto open_paren = header.find('(');
        const auto close_paren = header.find(')');

        if (open_paren != std::string_view::npos && close_paren != std::string_view::npos && close_paren > open_paren) {
            rec.type = std::string(trim(header.substr(0, open_paren)));
            rec.scope = std::string(trim(header.substr(open_paren + 1, close_paren - open_paren - 1)));
        } else {
            const auto clean_header = header.substr(0, header.find('!'));
            rec.type = std::string(trim(clean_header));
        }

        // Класифікація запису
        if (rec.is_breaking) {
            rec.category = Category::Breaking;
        } else if (!rec.cve.empty() || rec.type == "sec" || rec.scope == "sec") {
            rec.category = Category::Security;
        } else if (rec.type == "feat") {
            rec.category = Category::Feature;
        } else if (rec.type == "fix") {
            rec.category = Category::Fix;
        } else {
            rec.category = Category::Ignore;
        }

        return rec;
    }

    static void render_markdown(std::string_view version, std::string_view date, const std::vector<std::string_view>& raw_commits) {
        std::vector<CommitRecord> entries;
        entries.reserve(raw_commits.size());

        for (const auto& raw : raw_commits) {
            if (auto rec = parse_commit(raw); rec.category != Category::Ignore) {
                entries.push_back(std::move(rec));
            }
        }

        std::cout << "# Нотатки випуску " << version << " (" << date << ")\n\n";

        static constexpr std::array<std::string_view, static_cast<size_t>(Category::Count)> headers = {
            "## 🔴 Обов'язкові дії та несумісні зміни (Breaking Changes)",
            "## 🔒 Бюлетені безпеки (Security Advisories)",
            "## ✨ Нові можливості (Features)",
            "## 🐛 Виправлення дефектів (Bug Fixes)",
            ""
        };

        for (size_t cat_idx = 0; cat_idx < static_cast<size_t>(Category::Ignore); ++cat_idx) {
            const auto current_cat = static_cast<Category>(cat_idx);
            bool section_opened = false;

            for (const auto& entry : entries) {
                if (entry.category == current_cat) {
                    if (!section_opened) {
                        std::cout << headers[cat_idx] << "\n\n";
                        section_opened = true;
                    }
                    if (!entry.scope.empty()) {
                        std::cout << "- **" << entry.scope << ":** " << entry.description;
                    } else {
                        std::cout << "- " << entry.description;
                    }

                    if (!entry.cve.empty()) {
                        std::cout << " (`" << entry.cve << "`)";
                    }
                    std::cout << "\n";
                }
            }
            if (section_opened) {
                std::cout << "\n";
            }
        }
    }
};

int main() {
    const std::vector<std::string_view> commits = {
        "feat(can)!: перейти на бітову швидкість CAN-FD 2 Мбіт/с",
        "fix(adc): виправити дрейф нульового рівня входу АЦП",
        "fix(sec): усунути переповнення буфера Modbus (CVE-2026-4412)",
        "chore(ci): оновити версію компілятора GCC до 14.2",
        "feat(telemetry): додати періодичний звіт про стан акумулятора",
        "docs(readme): оновити схему підключення UART"
    };

    ReleaseNotesGenerator::render_markdown("v3.2.0", "2026-08-28", commits);
    return 0;
}
