// cookie_engine.hpp
#pragma once
#include <string>
#include <string_view>
#include <unordered_map>
#include <optional>
#include <expected>
#include <vector>
#include <sstream>
#include <iomanip>
#include <cctype>

namespace web {

enum class SameSiteMode {
    Strict,
    Lax,
    None
};

struct CookieOptions {
    std::optional<int64_t> max_age;
    std::optional<std::string> domain;
    std::optional<std::string> path;
    bool secure = false;
    bool http_only = false;
    std::optional<SameSiteMode> same_site;
    bool partitioned = false;
};

class CookieEngine {
public:
    // Безпечне URL-декодування без падіння на некоректних байтах
    static std::string url_decode(std::string_view in) {
        std::string out;
        out.reserve(in.size());
        for (size_t i = 0; i < in.size(); ++i) {
            if (in[i] == '%' && i + 2 < in.size()) {
                auto hex_val = [](char c) -> int {
                    if (c >= '0' && c <= '9') return c - '0';
                    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
                    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
                    return -1;
                };
                int hi = hex_val(in[i + 1]);
                int lo = hex_val(in[i + 2]);
                if (hi != -1 && lo != -1) {
                    out.push_back(static_cast<char>((hi << 4) | lo));
                    i += 2;
                    continue;
                }
            } else if (in[i] == '+') {
                out.push_back(' ');
                continue;
            }
            out.push_back(in[i]);
        }
        return out;
    }

    // URL-кодування рядка
    static std::string url_encode(std::string_view in) {
        std::ostringstream ss;
        for (unsigned char c : in) {
            if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
                ss << c;
            } else {
                ss << '%' << std::uppercase << std::hex << std::setw(2)
                   << std::setfill('0') << static_cast<int>(c);
            }
        }
        return ss.str();
    }

    // Парсер вхідного заголовка Cookie
    static std::unordered_map<std::string, std::string> parse(std::string_view header) {
        std::unordered_map<std::string, std::string> cookies;
        size_t start = 0;

        while (start < header.size()) {
            size_t end = header.find(';', start);
            if (end == std::string_view::npos) end = header.size();

            std::string_view token = header.substr(start, end - start);
            // Видалення пробілів
            while (!token.empty() && std::isspace(static_cast<unsigned char>(token.front())))
                token.remove_prefix(1);
            while (!token.empty() && std::isspace(static_cast<unsigned char>(token.back())))
                token.remove_suffix(1);

            if (!token.empty()) {
                size_t eq = token.find('=');
                if (eq != std::string_view::npos) {
                    std::string_view k = token.substr(0, eq);
                    std::string_view v = token.substr(eq + 1);

                    // Зняття лапок
                    if (v.size() >= 2 && v.front() == '"' && v.back() == '"') {
                        v = v.substr(1, v.size() - 2);
                    }

                    std::string key = url_decode(k);
                    std::string val = url_decode(v);
                    if (!key.empty() && !cookies.contains(key)) {
                        cookies.emplace(std::move(key), std::move(val));
                    }
                }
            }
            start = end + 1;
        }
        return cookies;
    }

    // Серіалізатор Set-Cookie з верифікацією префіксів
    static std::expected<std::string, std::string> serialize(
        std::string_view name,
        std::string_view value,
        const CookieOptions& opts
    ) {
        if (name.empty()) {
            return std::unexpected("Ім'я cookie не може бути порожнім");
        }

        // Перевірка префіксів RFC 6265bis
        if (name.starts_with("__Secure-")) {
            if (!opts.secure) {
                return std::unexpected("Префікс __Secure- вимагає прапорця secure");
            }
        }

        if (name.starts_with("__Host-")) {
            if (!opts.secure) {
                return std::unexpected("Префікс __Host- вимагає прапорця secure");
            }
            if (opts.domain.has_value()) {
                return std::unexpected("Префікс __Host- забороняє встановлювати domain");
            }
            if (!opts.path.has_value() || opts.path.value() != "/") {
                return std::unexpected("Префікс __Host- вимагає path = '/'");
            }
        }

        std::string out;
        out.reserve(128);
        out.append(name);
        out.push_back('=');
        out.append(url_encode(value));

        if (opts.max_age.has_value()) {
            out.append("; Max-Age=");
            out.append(std::to_string(opts.max_age.value()));
        }

        if (opts.domain.has_value()) {
            out.append("; Domain=");
            out.append(opts.domain.value());
        }

        if (opts.path.has_value()) {
            out.append("; Path=");
            out.append(opts.path.value());
        }

        if (opts.http_only) {
            out.append("; HttpOnly");
        }

        if (opts.secure) {
            out.append("; Secure");
        }

        if (opts.same_site.has_value()) {
            if (opts.same_site.value() == SameSiteMode::None && !opts.secure) {
                return std::unexpected("SameSite=None вимагає прапорця secure");
            }
            out.append("; SameSite=");
            switch (opts.same_site.value()) {
                case SameSiteMode::Strict: out.append("Strict"); break;
                case SameSiteMode::Lax:    out.append("Lax"); break;
                case SameSiteMode::None:   out.append("None"); break;
            }
        }

        if (opts.partitioned) {
            out.append("; Partitioned");
        }

        return out;
    }
};

} // namespace web
