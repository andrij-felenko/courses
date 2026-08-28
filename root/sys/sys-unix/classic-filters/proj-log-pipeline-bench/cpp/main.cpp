#include <iostream>
#include <fstream>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>

struct StringHash {
    using is_transparent = void;
    std::size_t operator()(std::string_view sv) const noexcept {
        return std::hash<std::string_view>{}(sv);
    }
};

void analyze_stream(int fd) {
    constexpr std::size_t kBufSize = 64 * 1024;
    std::vector<char> buffer(kBufSize + 1);
    std::unordered_map<std::string, std::size_t> ip_counts;
    
    std::size_t carry = 0;
    ssize_t bytes_read = 0;

    while ((bytes_read = ::read(fd, buffer.data() + carry, kBufSize - carry)) > 0) {
        std::size_t total = carry + static_cast<std::size_t>(bytes_read);
        buffer[total] = '\0';
        
        std::size_t line_start = 0;
        while (true) {
            const char* nl = static_cast<const char*>(
                std::memchr(buffer.data() + line_start, '\n', total - line_start)
            );
            if (!nl) break;

            std::size_t line_end = nl - buffer.data();
            std::string_view line(buffer.data() + line_start, line_end - line_start);
            
            // Парсинг $1 (IP) та $9 (Status) без додаткових алокацій
            auto sp1 = line.find(' ');
            if (sp1 != std::string_view::npos) {
                std::string_view ip = line.substr(0, sp1);
                std::size_t pos = sp1 + 1;
                int field = 2;
                while (field < 9 && pos < line.size()) {
                    pos = line.find(' ', pos);
                    if (pos == std::string_view::npos) break;
                    pos++;
                    field++;
                }
                if (field == 9 && pos + 3 <= line.size()) {
                    std::string_view status = line.substr(pos, 3);
                    if (status.size() >= 3 && status[0] == '5' &&
                        status[1] >= '0' && status[1] <= '9' &&
                        status[2] >= '0' && status[2] <= '9') {
                        ip_counts[std::string(ip)]++;
                    }
                }
            }
            line_start = line_end + 1;
        }
        carry = total - line_start;
        std::memmove(buffer.data(), buffer.data() + line_start, carry);
    }
}
