#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <system_error>

enum class SysuserType : char {
    User = 'u',
    Group = 'g',
    Member = 'm',
    Range = 'r',
    Unknown = '\0'
};

struct SysuserEntry {
    SysuserType type{SysuserType::Unknown};
    std::string name;
    std::string id;
    std::string gecos;
    std::string home;
    std::string shell;
    bool force_fatal{false};
};

class SysusersParser {
public:
    static std::optional<SysuserEntry> parseLine(std::string_view line) {
        line = trim(line);
        if (line.empty() || line.starts_with('#')) {
            return std::nullopt;
        }

        SysuserEntry entry;
        auto tokens = tokenize(line);
        if (tokens.empty()) {
            return std::nullopt;
        }

        if (tokens[0].size() != 1) {
            return std::nullopt;
        }

        char t = tokens[0][0];
        if (t != 'u' && t != 'g' && t != 'm' && t != 'r') {
            return std::nullopt;
        }
        entry.type = static_cast<SysuserType>(t);

        if (tokens.size() > 1) {
            std::string_view name_token = tokens[1];
            if (name_token.starts_with('!')) {
                entry.force_fatal = true;
                name_token.remove_prefix(1);
            }
            entry.name = std::string(name_token);
        }

        if (entry.type == SysuserType::User) {
            if (tokens.size() > 2) entry.id = std::string(tokens[2]);
            if (tokens.size() > 3) entry.gecos = std::string(tokens[3]);
            if (tokens.size() > 4) entry.home = std::string(tokens[4]);
            if (tokens.size() > 5) entry.shell = std::string(tokens[5]);
        } else if (entry.type == SysuserType::Group || entry.type == SysuserType::Range) {
            if (tokens.size() > 2) entry.id = std::string(tokens[2]);
        } else if (entry.type == SysuserType::Member) {
            if (tokens.size() > 2) entry.id = std::string(tokens[2]);
        }

        return entry;
    }

private:
    static std::string_view trim(std::string_view sv) {
        while (!sv.empty() && std::isspace(static_cast<unsigned char>(sv.front()))) {
            sv.remove_prefix(1);
        }
        while (!sv.empty() && std::isspace(static_cast<unsigned char>(sv.back()))) {
            sv.remove_suffix(1);
        }
        return sv;
    }

    static std::vector<std::string_view> tokenize(std::string_view sv) {
        std::vector<std::string_view> tokens;
        bool in_quotes = false;
        size_t start = 0;

        for (size_t i = 0; i < sv.size(); ++i) {
            char ch = sv[i];
            if (ch == '"') {
                in_quotes = !in_quotes;
            } else if (!in_quotes && std::isspace(static_cast<unsigned char>(ch))) {
                if (i > start) {
                    tokens.push_back(stripQuotes(sv.substr(start, i - start)));
                }
                start = i + 1;
            }
        }
        if (start < sv.size()) {
            tokens.push_back(stripQuotes(sv.substr(start)));
        }
        return tokens;
    }

    static std::string_view stripQuotes(std::string_view token) {
        if (token.size() >= 2 && token.front() == '"' && token.back() == '"') {
            token.remove_prefix(1);
            token.remove_suffix(1);
        }
        return token;
    }
};
