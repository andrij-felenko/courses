// dco_verifier.cpp — Ідіоматичний валідатор DCO на сучасному C++ (C++20)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <regex>
#include <algorithm>
#include <fstream>
#include <sstream>

enum class DcoError {
    None,
    MissingSignedOffBy,
    EmailMismatch,
    EmptyMessage,
    MalformedTrailer
};

struct Trailer {
    std::string key;
    std::string name;
    std::string email;
};

struct DcoReport {
    bool is_valid{false};
    DcoError error{DcoError::None};
    std::string expected_author;
    std::string matched_signature;
    std::vector<Trailer> trailers;

    [[nodiscard]] std::string to_json() const {
        std::ostringstream ss;
        if (is_valid) {
            ss << "{\"valid\":true,\"status\":\"ok\",\"signed_by\":\"" 
               << matched_signature << "\",\"trailers_count\":" << trailers.size() << "}";
        } else {
            ss << "{\"valid\":false,\"error\":\"";
            switch (error) {
                case DcoError::MissingSignedOffBy: ss << "missing_signed_off_by"; break;
                case DcoError::EmailMismatch:      ss << "email_mismatch"; break;
                case DcoError::EmptyMessage:       ss << "empty_commit_message"; break;
                default:                           ss << "unknown_error"; break;
            }
            ss << "\",\"expected\":\"" << expected_author << "\"}";
        }
        return ss.str();
    }
};

class DcoEngine {
public:
    static std::string trim(std::string_view sv) {
        auto start = sv.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return "";
        auto end = sv.find_last_not_of(" \t\r\n");
        return std::string(sv.substr(start, end - start + 1));
    }

    static bool iequals(std::string_view a, std::string_view b) {
        return std::ranges::equal(a, b, [](char ca, char cb) {
            return std::tolower(static_cast<unsigned char>(ca)) == 
                   std::tolower(static_cast<unsigned char>(cb));
        });
    }

    static std::optional<Trailer> parse_line(std::string_view line) {
        static const std::regex trailer_re(R"(^([A-Za-z0-9\-]+)\s*:\s*([^<]+)\s*<([^>]+)>\s*$)");
        std::string s_line = trim(line);
        std::smatch match;

        if (std::regex_match(s_line, match, trailer_re)) {
            return Trailer{
                .key = trim(match[1].str()),
                .name = trim(match[2].str()),
                .email = trim(match[3].str())
            };
        }
        return std::nullopt;
    }

    static DcoReport verify(std::string_view message, 
                            std::string_view author_name, 
                            std::string_view author_email) {
        DcoReport report;
        report.expected_author = std::string(author_name) + " <" + std::string(author_email) + ">";

        if (message.empty() || trim(message).empty()) {
            report.error = DcoError::EmptyMessage;
            return report;
        }

        // Розбиваємо текст на рядки без зайвого копіювання через string_view
        std::vector<std::string_view> lines;
        size_t pos = 0;
        while (pos < message.size()) {
            size_t next = message.find('\n', pos);
            if (next == std::string_view::npos) next = message.size();
            lines.push_back(message.substr(pos, next - pos));
            pos = next + 1;
        }

        // Шукаємо трейлери знизу вгору
        std::vector<Trailer> found_trailers;
        for (auto it = lines.rbegin(); it != lines.rend(); ++it) {
            std::string line_str = trim(*it);
            if (line_str.empty()) {
                if (!found_trailers.empty()) break; // Зустріли порожній рядок над блоком
                continue;
            }

            if (auto t = parse_line(*it); t.has_value()) {
                found_trailers.push_back(*std::move(t));
            } else {
                if (!found_trailers.empty()) break;
            }
        }

        report.trailers = found_trailers;

        // Пошук валідного Signed-off-by
        bool found_sob = false;
        for (const auto& tr : found_trailers) {
            if (iequals(tr.key, "Signed-off-by")) {
                found_sob = true;
                if (iequals(tr.email, author_email)) {
                    report.is_valid = true;
                    report.matched_signature = tr.name + " <" + tr.email + ">";
                    return report;
                }
            }
        }

        if (!found_sob) {
            report.error = DcoError::MissingSignedOffBy;
        } else {
            report.error = DcoError::EmailMismatch;
        }

        return report;
    }
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] 
                  << " <Author Name> <Author Email> [Commit Msg File]\n";
        return 2;
    }

    std::string author_name = argv[1];
    std::string author_email = argv[2];
    std::string message;

    if (argc >= 4) {
        std::ifstream file(argv[3], std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "Помилка читання файлу: " << argv[3] << "\n";
            return 2;
        }
        std::ostringstream ss;
        ss << file.rdbuf();
        message = ss.str();
    } else {
        std::ostringstream ss;
        ss << std::cin.rdbuf();
        message = ss.str();
    }

    auto report = DcoEngine::verify(message, author_name, author_email);
    std::cout << report.to_json() << "\n";

    return report.is_valid ? 0 : 1;
}
