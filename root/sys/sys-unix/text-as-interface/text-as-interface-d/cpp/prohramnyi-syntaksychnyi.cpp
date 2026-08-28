#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <charconv>
#include <vector>
#include <optional>

struct UserRecord {
    std::string username;
    unsigned int uid{0};
    unsigned int gid{0};
    std::string homedir;
    std::string shell;
};

// Безпечний безалокаційний синтаксичний розбір рядка за роздільником
std::optional<UserRecord> parse_passwd_line(std::string_view line) {
    if (line.empty() || line.starts_with('#')) {
        return std::nullopt;
    }

    std::vector<std::string_view> fields;
    size_t start = 0;
    while (start <= line.size()) {
        const size_t end = line.find(':', start);
        if (end == std::string_view::npos) {
            fields.push_back(line.substr(start));
            break;
        }
        fields.push_back(line.substr(start, end - start));
        start = end + 1;
    }

    if (fields.size() < 7) {
        return std::nullopt;
    }

    unsigned int uid = 0;
    unsigned int gid = 0;
    auto [p1, ec1] = std::from_chars(fields[2].data(), fields[2].data() + fields[2].size(), uid);
    auto [p2, ec2] = std::from_chars(fields[3].data(), fields[3].data() + fields[3].size(), gid);

    if (ec1 != std::errc{} || ec2 != std::errc{}) {
        return std::nullopt;
    }

    return UserRecord{
        .username = std::string(fields[0]),
        .uid = uid,
        .gid = gid,
        .homedir = std::string(fields[5]),
        .shell = std::string(fields[6])
    };
}

void parse_passwd_file(std::istream& input) {
    std::string line;
    while (std::getline(input, line)) {
        if (const auto record = parse_passwd_line(line)) {
            if (record->uid >= 1000) {
                std::cout << "Користувач: " << record->username 
                          << ", UID: " << record->uid 
                          << ", Home: " << record->homedir 
                          << ", Shell: " << record->shell << '\n';
            }
        }
    }
}
