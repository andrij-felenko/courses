#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <algorithm>
#include <regex>
#include <cctype>

struct NaptrRecord {
    uint16_t order;
    uint16_t preference;
    std::string flags;
    std::string service;
    std::string regexp;
    std::string replacement;
};

class EnumResolver {
public:
    // Перетворення міжнародного номера у доменне ім'я e164.arpa
    static std::optional<std::string> toEnumDomain(std::string_view e164Input) {
        std::string digits;
        digits.reserve(16);

        for (char ch : e164Input) {
            if (std::isdigit(static_cast<unsigned char>(ch))) {
                if (digits.size() >= 15) return std::nullopt; // Перевищення E.164
                digits.push_back(ch);
            }
        }
        if (digits.empty()) return std::nullopt;

        std::string domain;
        domain.reserve(digits.size() * 2 + 10);
        for (auto it = digits.rbegin(); it != digits.rend(); ++it) {
            domain.push_back(*it);
            domain.push_back('.');
        }
        domain.append("e164.arpa");
        return domain;
    }

    // Резолвінг найкращого SIP URI з набору записів NAPTR
    static std::optional<std::string> resolveSipUri(
        std::string_view e164Number,
        std::vector<NaptrRecord> records)
    {
        // Нормалізація вхідного ключа для зіставлення з регулярним виразом (+380...)
        std::string normalizedNumber = "+";
        for (char ch : e164Number) {
            if (std::isdigit(static_cast<unsigned char>(ch))) {
                normalizedNumber.push_back(ch);
            }
        }

        // Сортування за Order (зростання), потім Preference (зростання)
        std::ranges::sort(records, [](const NaptrRecord& a, const NaptrRecord& b) {
            if (a.order != b.order) return a.order < b.order;
            return a.preference < b.preference;
        });

        for (const auto& rec : records) {
            // Фільтрація: термінальний прапорець 'u' та сервіс SIP
            if (rec.flags != "u" && rec.flags != "U") continue;
            if (rec.service != "E2U+sip" && rec.service != "e2u+sip") continue;

            auto uri = applyRegexp(rec.regexp, normalizedNumber);
            if (uri) return uri;
        }

        return std::nullopt;
    }

private:
    static std::optional<std::string> applyRegexp(
        std::string_view regexpField,
        const std::string& inputKey)
    {
        if (regexpField.size() < 3) return std::nullopt;
        char delim = regexpField.front();

        auto firstSplit = regexpField.find(delim, 1);
        if (firstSplit == std::string_view::npos) return std::nullopt;

        auto secondSplit = regexpField.find(delim, firstSplit + 1);
        if (secondSplit == std::string_view::npos) return std::nullopt;

        std::string pattern(regexpField.substr(1, firstSplit - 1));
        std::string replacement(regexpField.substr(firstSplit + 1, secondSplit - firstSplit - 1));

        try {
            std::regex re(pattern, std::regex_constants::ECMAScript);
            // Заміна синтаксису зворотних посилань \1 -> $1 для std::regex_replace
            std::string fmt = replacement;
            for (size_t pos = 0; pos + 1 < fmt.size(); ++pos) {
                if (fmt[pos] == '\\' && std::isdigit(static_cast<unsigned char>(fmt[pos + 1]))) {
                    fmt[pos] = '$';
                }
            }

            if (std::regex_search(inputKey, re)) {
                return std::regex_replace(inputKey, re, fmt);
            }
        } catch (const std::regex_error&) {
            return std::nullopt;
        }

        return std::nullopt;
    }
};
