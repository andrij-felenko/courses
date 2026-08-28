#include <iostream>
#include <string_view>
#include <optional>
#include <charconv>

struct UrlParts {
    std::string_view scheme;
    std::string_view host;
    int port{80};
    std::string_view path{"/"};
    std::string_view query;
};

class FastUrlParser {
public:
    static std::optional<UrlParts> parse(std::string_view url) noexcept {
        UrlParts parts;
        auto scheme_pos = url.find("://");
        if (scheme_pos == std::string_view::npos) return std::nullopt;

        parts.scheme = url.substr(0, scheme_pos);
        url.remove_prefix(scheme_pos + 3);

        // Відокремлюємо authority від шляху
        auto path_pos = url.find_first_of("/?#");
        auto auth = (path_pos == std::string_view::npos) ? url : url.substr(0, path_pos);

        if (auto colon = auth.find(':'); colon != std::string_view::npos) {
            parts.host = auth.substr(0, colon);
            auto port_str = auth.substr(colon + 1);
            std::from_chars(port_str.data(), port_str.data() + port_str.size(), parts.port);
        } else {
            parts.host = auth;
            parts.port = (parts.scheme == "https") ? 443 : 80;
        }

        if (path_pos != std::string_view::npos) {
            url.remove_prefix(path_pos);
            auto query_pos = url.find('?');
            auto frag_pos = url.find('#');

            if (query_pos != std::string_view::npos) {
                parts.path = url.substr(0, query_pos);
                auto query_end = (frag_pos != std::string_view::npos) ? frag_pos : url.size();
                parts.query = url.substr(query_pos + 1, query_end - (query_pos + 1));
            } else if (frag_pos != std::string_view::npos) {
                parts.path = url.substr(0, frag_pos);
            } else {
                parts.path = url;
            }
        }

        return parts;
    }
};
