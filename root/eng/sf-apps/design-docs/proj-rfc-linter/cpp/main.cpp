#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <algorithm>

enum class RfcStatus {
    Unknown,
    Draft,
    Review,
    Approved,
    Rejected,
    InProgress,
    Implemented,
    Superseded
};

constexpr std::string_view to_string(RfcStatus s) noexcept {
    switch (s) {
        case RfcStatus::Draft: return "draft";
        case RfcStatus::Review: return "review";
        case RfcStatus::Approved: return "approved";
        case RfcStatus::Rejected: return "rejected";
        case RfcStatus::InProgress: return "in_progress";
        case RfcStatus::Implemented: return "implemented";
        case RfcStatus::Superseded: return "superseded";
        default: return "unknown";
    }
}

constexpr RfcStatus parse_status(std::string_view str) noexcept {
    if (str.find("draft") != std::string_view::npos) return RfcStatus::Draft;
    if (str.find("review") != std::string_view::npos) return RfcStatus::Review;
    if (str.find("approved") != std::string_view::npos) return RfcStatus::Approved;
    if (str.find("rejected") != std::string_view::npos) return RfcStatus::Rejected;
    if (str.find("in_progress") != std::string_view::npos) return RfcStatus::InProgress;
    if (str.find("implemented") != std::string_view::npos) return RfcStatus::Implemented;
    if (str.find("superseded") != std::string_view::npos) return RfcStatus::Superseded;
    return RfcStatus::Unknown;
}

struct RfcDocument {
    std::string rfc_id;
    std::string title;
    RfcStatus status{RfcStatus::Unknown};
    bool has_goals{false};
    bool has_non_goals{false};
    bool has_architecture{false};
    bool has_alternatives{false};
    bool has_migration{false};
    bool has_open_questions{false};
    int unresolved_questions_count{0};
    std::vector<std::string> defects;

    [[nodiscard]] bool is_valid() const noexcept {
        return defects.empty();
    }
};

class RfcValidator {
public:
    static RfcDocument validate_file(const std::string &path) {
        RfcDocument doc;
        std::ifstream file(path);
        if (!file.is_open()) {
            doc.defects.push_back("Не вдалося відкрити файл: " + path);
            return doc;
        }

        std::string line;
        int line_number = 0;
        bool in_frontmatter = false;
        bool frontmatter_closed = false;
        bool in_code_block = false;
        bool in_open_questions = false;

        while (std::getline(file, line)) {
            line_number++;
            std::string_view sv = trim(line);

            // Ігнорування рядків усередині блоків коду
            if (sv.size() >= 3 && sv[0] == '`' && sv[1] == '`' && sv[2] == '`') {
                in_code_block = !in_code_block;
                continue;
            }
            if (in_code_block) {
                continue;
            }

            if (line_number == 1 && sv == "---") {
                in_frontmatter = true;
                continue;
            }

            if (in_frontmatter) {
                if (sv == "---") {
                    in_frontmatter = false;
                    frontmatter_closed = true;
                    continue;
                }
                parse_frontmatter_line(sv, doc);
                continue;
            }

            if (sv.starts_with("## ")) {
                in_open_questions = false;
                std::string_view header = sv.substr(3);

                if (contains_any(header, {"Цілі", "Goals"})) doc.has_goals = true;
                if (contains_any(header, {"Не-цілі", "Non-Goals", "не-цілі"})) doc.has_non_goals = true;
                if (contains_any(header, {"Архітектур", "Architecture", "дизайн"})) doc.has_architecture = true;
                if (contains_any(header, {"Альтернатив", "Alternatives"})) doc.has_alternatives = true;
                if (contains_any(header, {"Міграц", "Migration", "Rollout"})) doc.has_migration = true;
                if (contains_any(header, {"Відкриті питання", "Open Questions"})) {
                    doc.has_open_questions = true;
                    in_open_questions = true;
                }
            }

            if (in_open_questions && (sv.contains("- [ ]") || sv.contains("* [ ]"))) {
                doc.unresolved_questions_count++;
            }
        }

        // Перевірка інваріантів якості
        if (!frontmatter_closed) {
            doc.defects.emplace_back("Відсутній або незакритий блок метаданих frontmatter (---)");
        }
        if (doc.rfc_id.empty()) {
            doc.defects.emplace_back("Не вказано rfc_id у метаданих");
        }
        if (doc.status == RfcStatus::Unknown) {
            doc.defects.emplace_back("Некоректний або відсутній статус RFC");
        }
        if (!doc.has_goals || !doc.has_non_goals) {
            doc.defects.emplace_back("Відсутній обов'язковий розділ «Цілі та не-цілі (Goals & Non-Goals)»");
        }
        if (!doc.has_architecture) {
            doc.defects.emplace_back("Відсутній розділ архітектурного дизайну");
        }
        if (!doc.has_alternatives) {
            doc.defects.emplace_back("Відсутній розділ розглянутих альтернатив");
        }
        if (!doc.has_migration) {
            doc.defects.emplace_back("Відсутній план міграції та відкату (Rollout & Migration)");
        }
        if (doc.status == RfcStatus::Approved && doc.unresolved_questions_count > 0) {
            doc.defects.emplace_back("Статус 'approved', але зафіксовано " +
                                     std::to_string(doc.unresolved_questions_count) +
                                     " невирішених відкритих питань (- [ ])");
        }

        return doc;
    }

private:
    static std::string_view trim(std::string_view s) noexcept {
        const auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        const auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }

    static bool contains_any(std::string_view src, std::initializer_list<std::string_view> targets) noexcept {
        return std::ranges::any_of(targets, [&](std::string_view t) {
            return src.find(t) != std::string_view::npos;
        });
    }

    static void parse_frontmatter_line(std::string_view line, RfcDocument &doc) {
        if (line.starts_with("rfc_id:")) {
            doc.rfc_id = extract_value(line.substr(7));
        } else if (line.starts_with("title:")) {
            doc.title = extract_value(line.substr(6));
        } else if (line.starts_with("status:")) {
            doc.status = parse_status(extract_value(line.substr(7)));
        }
    }

    static std::string extract_value(std::string_view raw) {
        auto val = trim(raw);
        if (val.starts_with('"') && val.ends_with('"') && val.size() >= 2) {
            val = val.substr(1, val.size() - 2);
        }
        return std::string(val);
    }
};

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях-до-rfc.md>\n";
        return 1;
    }

    std::cout << "Валідація інженерної пропозиції: " << argv[1] << "\n";
    const auto doc = RfcValidator::validate_file(argv[1]);

    std::cout << "\nПідсумок аналізу:\n"
              << "  ID:        " << (doc.rfc_id.empty() ? "N/A" : doc.rfc_id) << "\n"
              << "  Назва:     " << (doc.title.empty() ? "N/A" : doc.title) << "\n"
              << "  Статус:    " << to_string(doc.status) << "\n"
              << "  Дефектів:  " << doc.defects.size() << "\n";

    if (doc.is_valid()) {
        std::cout << "\nРЕЗУЛЬТАТ: Пропозиція відповідає стандартам інженерного проектування.\n";
        return 0;
    }

    std::cout << "\nЗнайдені дефекти:\n";
    for (const auto &d : doc.defects) {
        std::cout << "  • " << d << "\n";
    }
    std::cout << "\nРЕЗУЛЬТАТ: Пропозиція блокується до виправлення зауважень.\n";
    return 1;
}
