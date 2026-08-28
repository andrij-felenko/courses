#include <iostream>
#include <string_view>
#include <optional>
#include <string>
#include <cctype>
#include <charconv>

struct ParsedUrl {
    std::string_view scheme;
    std::string_view userinfo;
    std::string_view host;
    int port{0};
    std::string_view path;
    std::string_view query;
    std::string_view fragment;
};

class UrlParser {
public:
    static std::optional<ParsedUrl> parse(std::string_view raw) noexcept {
        ParsedUrl url;
        std::string_view cur = raw;

        // 1. Схема
        if (auto colon = cur.find(':'); colon != std::string_view::npos) {
            auto candidate = cur.substr(0, colon);
            if (is_valid_scheme(candidate)) {
                url.scheme = candidate;
                cur.remove_prefix(colon + 1);
            }
        }

        // 2. Authority
        if (cur.starts_with("//")) {
            cur.remove_prefix(2);
            auto auth_end = cur.find_first_of("/?#");
            auto auth = (auth_end == std::string_view::npos) ? cur : cur.substr(0, auth_end);

            if (auto at = auth.find('@'); at != std::string_view::npos) {
                url.userinfo = auth.substr(0, at);
                auth.remove_prefix(at + 1);
            }

            // Host і Port
            if (auth.starts_with('[')) {
                // IPv6
                auto close_bracket = auth.find(']');
                if (close_bracket == std::string_view::npos) return std::nullopt;
                url.host = auth.substr(0, close_bracket + 1);
                auto after_host = auth.substr(close_bracket + 1);
                if (after_host.starts_with(':')) {
                    after_host.remove_prefix(1);
                    std::from_chars(after_host.data(), after_host.data() + after_host.size(), url.port);
                }
            } else {
                if (auto port_colon = auth.find(':'); port_colon != std::string_view::npos) {
                    url.host = auth.substr(0, port_colon);
                    auto port_str = auth.substr(port_colon + 1);
                    std::from_chars(port_str.data(), port_str.data() + port_str.size(), url.port);
                } else {
                    url.host = auth;
                }
            }

            cur = (auth_end == std::string_view::npos) ? std::string_view{} : cur.substr(auth_end);
        }

        // 3. Path
        auto path_end = cur.find_first_of("?#");
        url.path = (path_end == std::string_view::npos) ? cur : cur.substr(0, path_end);
        cur = (path_end == std::string_view::npos) ? std::string_view{} : cur.substr(path_end);

        // 4. Query
        if (cur.starts_with('?')) {
            cur.remove_prefix(1);
            auto query_end = cur.find('#');
            url.query = (query_end == std::string_view::npos) ? cur : cur.substr(0, query_end);
            cur = (query_end == std::string_view::npos) ? std::string_view{} : cur.substr(query_end);
        }

        // 5. Fragment
        if (cur.starts_with('#')) {
            url.fragment = cur.substr(1);
        }

        return url;
    }

private:
    static bool is_valid_scheme(std::string_view s) noexcept {
        if (s.empty() || !std::isalpha(static_cast<unsigned char>(s.front()))) return false;
        for (char c : s) {
            if (!std::isalnum(static_cast<unsigned char>(c)) && c != '+' && c != '-' && c != '.') {
                return false;
            }
        }
        return true;
    }
};
