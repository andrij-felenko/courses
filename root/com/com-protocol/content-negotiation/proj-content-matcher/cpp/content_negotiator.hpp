// content_negotiator.hpp — Високопродуктивний рушій C++20 без динамічних алокацій у гарячому циклі
#pragma once
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <optional>
#include <algorithm>
#include <charconv>

struct MediaRange {
    std::string type;
    std::string subtype;
    std::map<std::string, std::string> params;
    double q = 1.0;
    int specificity = 0;
    std::size_t clientIndex = 0;
};

struct LanguageRange {
    std::string tag;
    std::string primary;
    double q = 1.0;
    std::size_t clientIndex = 0;
};

struct MatchResult {
    std::string selectedType;
    double q = 1.0;
    std::vector<std::string> vary;
};

struct LanguageMatchResult {
    std::string selectedLanguage;
    double q = 1.0;
    std::vector<std::string> vary;
};

class ContentNegotiator {
public:
    explicit ContentNegotiator(std::vector<std::string> availableTypes,
                               std::vector<std::string> availableLanguages = {})
        : m_availableTypes(std::move(availableTypes)),
          m_availableLanguages(std::move(availableLanguages)) {
        for (auto& t : m_availableTypes) {
            std::transform(t.begin(), t.end(), t.begin(), [](unsigned char c) {
                return static_cast<char>(std::tolower(c));
            });
        }
        for (auto& l : m_availableLanguages) {
            std::transform(l.begin(), l.end(), l.begin(), [](unsigned char c) {
                return static_cast<char>(std::tolower(c));
            });
        }
    }

    std::vector<MediaRange> parseAccept(std::string_view header) const {
        if (header.empty()) {
            return { MediaRange{ "*", "*", {}, 1.0, 0, 0 } };
        }

        std::vector<MediaRange> ranges;
        std::size_t clientIdx = 0;
        std::size_t pos = 0;

        while (pos < header.size()) {
            std::size_t commaPos = findNextComma(header, pos);
            std::string_view entry = trim(header.substr(pos, commaPos - pos));
            pos = (commaPos == std::string_view::npos) ? header.size() : commaPos + 1;

            if (entry.empty()) continue;

            MediaRange range;
            range.clientIndex = clientIdx++;
            range.q = 1.0;

            std::size_t pStart = 0;
            bool isMimePart = true;

            while (pStart < entry.size()) {
                auto pEnd = entry.find(';', pStart);
                if (pEnd == std::string_view::npos) pEnd = entry.size();

                std::string_view part = trim(entry.substr(pStart, pEnd - pStart));
                pStart = pEnd + 1;

                if (part.empty()) continue;

                if (isMimePart) {
                    auto slash = part.find('/');
                    if (slash != std::string_view::npos) {
                        range.type = toLower(trim(part.substr(0, slash)));
                        range.subtype = toLower(trim(part.substr(slash + 1)));
                    }
                    isMimePart = false;
                } else {
                    auto eq = part.find('=');
                    if (eq != std::string_view::npos) {
                        std::string key = toLower(trim(part.substr(0, eq)));
                        std::string_view val = trim(part.substr(eq + 1));

                        if (val.size() >= 2 && val.front() == '"' && val.back() == '"') {
                            val = val.substr(1, val.size() - 2);
                        }

                        if (key == "q") {
                            double parsedQ = 1.0;
                            auto [ptr, ec] = std::from_chars(val.data(), val.data() + val.size(), parsedQ);
                            if (ec == std::errc()) {
                                range.q = std::clamp(parsedQ, 0.0, 1.0);
                            }
                        } else {
                            range.params[key] = std::string(val);
                        }
                    }
                }
            }

            if (range.type.empty() || range.subtype.empty()) continue;

            if (range.type == "*") {
                range.specificity = 0;
            } else if (range.subtype == "*") {
                range.specificity = 1;
            } else {
                range.specificity = range.params.empty() ? 2 : 3;
            }

            ranges.push_back(std::move(range));
        }

        std::sort(ranges.begin(), ranges.end(), [](const MediaRange& a, const MediaRange& b) {
            if (a.q != b.q) return a.q > b.q;
            if (a.specificity != b.specificity) return a.specificity > b.specificity;
            return a.clientIndex < b.clientIndex;
        });

        return ranges;
    }

    std::vector<LanguageRange> parseAcceptLanguage(std::string_view header) const {
        if (header.empty()) {
            return { LanguageRange{ "*", "*", 1.0, 0 } };
        }

        std::vector<LanguageRange> ranges;
        std::size_t clientIdx = 0;
        std::size_t pos = 0;

        while (pos < header.size()) {
            std::size_t commaPos = findNextComma(header, pos);
            std::string_view entry = trim(header.substr(pos, commaPos - pos));
            pos = (commaPos == std::string_view::npos) ? header.size() : commaPos + 1;

            if (entry.empty()) continue;

            LanguageRange range;
            range.clientIndex = clientIdx++;
            range.q = 1.0;

            auto semicolon = entry.find(';');
            std::string_view tagPart = trim(entry.substr(0, semicolon));
            range.tag = toLower(tagPart);

            auto dash = range.tag.find('-');
            range.primary = (dash == std::string::npos) ? range.tag : range.tag.substr(0, dash);

            if (semicolon != std::string_view::npos) {
                std::string_view paramPart = trim(entry.substr(semicolon + 1));
                auto eq = paramPart.find('=');
                if (eq != std::string_view::npos && toLower(trim(paramPart.substr(0, eq))) == "q") {
                    std::string_view val = trim(paramPart.substr(eq + 1));
                    double parsedQ = 1.0;
                    auto [ptr, ec] = std::from_chars(val.data(), val.data() + val.size(), parsedQ);
                    if (ec == std::errc()) {
                        range.q = std::clamp(parsedQ, 0.0, 1.0);
                    }
                }
            }

            ranges.push_back(std::move(range));
        }

        std::sort(ranges.begin(), ranges.end(), [](const LanguageRange& a, const LanguageRange& b) {
            if (a.q != b.q) return a.q > b.q;
            return a.clientIndex < b.clientIndex;
        });

        return ranges;
    }

    std::optional<MatchResult> negotiate(std::string_view acceptHeader) const {
        auto ranges = parseAccept(acceptHeader);

        for (const auto& range : ranges) {
            if (range.q <= 0.0) continue;

            for (const auto& serverType : m_availableTypes) {
                auto slash = serverType.find('/');
                if (slash == std::string::npos) continue;

                std::string_view sType(serverType.data(), slash);
                std::string_view sSubtype(serverType.data() + slash + 1, serverType.size() - slash - 1);

                bool typeMatch = (range.type == "*" || range.type == sType);
                bool subtypeMatch = (range.subtype == "*" || range.subtype == sSubtype);

                if (typeMatch && subtypeMatch) {
                    return MatchResult{
                        .selectedType = serverType,
                        .q = range.q,
                        .vary = { "Accept" }
                    };
                }
            }
        }

        return std::nullopt;
    }

    std::optional<LanguageMatchResult> negotiateLanguage(std::string_view acceptLanguageHeader) const {
        if (m_availableLanguages.empty()) return std::nullopt;

        auto ranges = parseAcceptLanguage(acceptLanguageHeader);

        for (const auto& range : ranges) {
            if (range.q <= 0.0) continue;

            for (const auto& lang : m_availableLanguages) {
                if (range.tag == "*" || lang == range.tag) {
                    return LanguageMatchResult{
                        .selectedLanguage = lang,
                        .q = range.q,
                        .vary = { "Accept-Language" }
                    };
                }
            }

            for (const auto& lang : m_availableLanguages) {
                auto dash = lang.find('-');
                std::string_view sPrimary = (dash == std::string::npos) ? std::string_view(lang) : std::string_view(lang.data(), dash);
                if (range.primary == sPrimary) {
                    return LanguageMatchResult{
                        .selectedLanguage = lang,
                        .q = range.q,
                        .vary = { "Accept-Language" }
                    };
                }
            }
        }

        return LanguageMatchResult{
            .selectedLanguage = m_availableLanguages.front(),
            .q = 1.0,
            .vary = { "Accept-Language" }
        };
    }

private:
    std::vector<std::string> m_availableTypes;
    std::vector<std::string> m_availableLanguages;

    static std::size_t findNextComma(std::string_view str, std::size_t start) {
        bool inQuotes = false;
        for (std::size_t i = start; i < str.size(); ++i) {
            if (str[i] == '"' && (i == 0 || str[i - 1] != '\\')) {
                inQuotes = !inQuotes;
            } else if (str[i] == ',' && !inQuotes) {
                return i;
            }
        }
        return std::string_view::npos;
    }

    static std::string_view trim(std::string_view s) {
        while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) s.remove_prefix(1);
        while (!s.empty() && (s.back() == ' ' || s.back() == '\t')) s.remove_suffix(1);
        return s;
    }

    static std::string toLower(std::string_view s) {
        std::string res(s);
        std::transform(res.begin(), res.end(), res.begin(), [](unsigned char c) {
            return static_cast<char>(std::tolower(c));
        });
        return res;
    }
};
