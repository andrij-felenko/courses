#include <iostream>
#include <string>
#include <optional>

class AtGpioParser {
public:
    static std::optional<int> parseReadResponse(const std::string &response) {
        size_t pos = response.find("+SYSGPIOREAD:");
        if (pos != std::string::npos) {
            size_t comma = response.find(',', pos);
            if (comma != std::string::npos) {
                int val = std::stoi(response.substr(comma + 1));
                return val;
            }
        }
        return std::nullopt;
    }
};
