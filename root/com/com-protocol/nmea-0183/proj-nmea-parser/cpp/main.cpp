#include <iostream>
#include <string_view>
#include <vector>
#include <optional>
#include <charconv>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>

struct NmeaGga {
    double utc_time{0.0};
    double latitude{0.0};
    double longitude{0.0};
    uint8_t fix_quality{0};
    uint8_t satellites{0};
    float hdop{99.9f};
    float altitude{0.0f};
    float geoid_sep{0.0f};
};

struct NmeaRmc {
    double utc_time{0.0};
    bool is_valid{false};
    double latitude{0.0};
    double longitude{0.0};
    float speed_knots{0.0f};
    float speed_mps{0.0f};
    float course_deg{0.0f};
    uint32_t date_dmyt{0};
    char faa_mode{'N'};
};

class NmeaParser {
public:
    enum class State {
        WaitStart,
        ReadPayload,
        ReadCs1,
        ReadCs2,
        WaitCr,
        WaitLf
    };

    std::optional<std::string_view> feed(uint8_t byte) noexcept {
        if (byte == '$' || byte == '!') {
            state_ = State::ReadPayload;
            buf_idx_ = 0;
            calc_crc_ = 0;
            return std::nullopt;
        }

        switch (state_) {
            case State::WaitStart:
                return std::nullopt;

            case State::ReadPayload:
                if (byte == '*') {
                    buffer_[buf_idx_] = '\0';
                    state_ = State::ReadCs1;
                } else if (byte == '\r' || byte == '\n') {
                    state_ = State::WaitStart;
                    errors_++;
                } else {
                    if (buf_idx_ < buffer_.size() - 1) {
                        buffer_[buf_idx_++] = static_cast<char>(byte);
                        calc_crc_ ^= byte;
                    } else {
                        state_ = State::WaitStart;
                        errors_++;
                    }
                }
                return std::nullopt;

            case State::ReadCs1: {
                int v = hexToVal(static_cast<char>(byte));
                if (v >= 0) {
                    rx_crc_ = static_cast<uint8_t>(v << 4);
                    state_ = State::ReadCs2;
                } else {
                    state_ = State::WaitStart;
                    errors_++;
                }
                return std::nullopt;
            }

            case State::ReadCs2: {
                int v = hexToVal(static_cast<char>(byte));
                if (v >= 0) {
                    rx_crc_ |= static_cast<uint8_t>(v);
                    if (rx_crc_ == calc_crc_) {
                        state_ = State::WaitCr;
                    } else {
                        state_ = State::WaitStart;
                        errors_++;
                    }
                } else {
                    state_ = State::WaitStart;
                    errors_++;
                }
                return std::nullopt;
            }

            case State::WaitCr:
                if (byte == '\r') {
                    state_ = State::WaitLf;
                } else if (byte == '\n') {
                    state_ = State::WaitStart;
                    success_++;
                    return std::string_view(buffer_.data(), buf_idx_);
                } else {
                    state_ = State::WaitStart;
                    errors_++;
                }
                return std::nullopt;

            case State::WaitLf:
                state_ = State::WaitStart;
                if (byte == '\n') {
                    success_++;
                    return std::string_view(buffer_.data(), buf_idx_);
                }
                errors_++;
                return std::nullopt;
        }
        return std::nullopt;
    }

    [[nodiscard]] uint32_t successCount() const noexcept { return success_; }
    [[nodiscard]] uint32_t errorCount() const noexcept { return errors_; }

    static std::optional<NmeaGga> parseGga(std::string_view line) noexcept {
        std::array<std::string_view, 20> fields{};
        size_t field_cnt = splitFields(line, fields);

        if (field_cnt < 10 || !fields[0].ends_with("GGA")) {
            return std::nullopt;
        }

        NmeaGga gga{};
        if (!fields[1].empty()) gga.utc_time = parseDouble(fields[1]);
        if (!fields[2].empty() && !fields[3].empty()) {
            gga.latitude = parseCoordinate(fields[2], fields[3][0]);
        }
        if (!fields[4].empty() && !fields[5].empty()) {
            gga.longitude = parseCoordinate(fields[4], fields[5][0]);
        }
        if (!fields[6].empty()) gga.fix_quality = static_cast<uint8_t>(parseInt(fields[6]));
        if (!fields[7].empty()) gga.satellites  = static_cast<uint8_t>(parseInt(fields[7]));
        if (!fields[8].empty()) gga.hdop        = static_cast<float>(parseDouble(fields[8]));
        if (!fields[9].empty()) gga.altitude    = static_cast<float>(parseDouble(fields[9]));
        if (field_cnt > 11 && !fields[11].empty()) {
            gga.geoid_sep = static_cast<float>(parseDouble(fields[11]));
        }

        return gga;
    }

    static std::optional<NmeaRmc> parseRmc(std::string_view line) noexcept {
        std::array<std::string_view, 20> fields{};
        size_t field_cnt = splitFields(line, fields);

        if (field_cnt < 10 || !fields[0].ends_with("RMC")) {
            return std::nullopt;
        }

        NmeaRmc rmc{};
        if (!fields[1].empty()) rmc.utc_time = parseDouble(fields[1]);
        rmc.is_valid = (!fields[2].empty() && fields[2][0] == 'A');
        if (!fields[3].empty() && !fields[4].empty()) {
            rmc.latitude = parseCoordinate(fields[3], fields[4][0]);
        }
        if (!fields[5].empty() && !fields[6].empty()) {
            rmc.longitude = parseCoordinate(fields[5], fields[6][0]);
        }
        if (!fields[7].empty()) {
            rmc.speed_knots = static_cast<float>(parseDouble(fields[7]));
            rmc.speed_mps = rmc.speed_knots * 0.51444444f;
        }
        if (!fields[8].empty()) rmc.course_deg = static_cast<float>(parseDouble(fields[8]));
        if (!fields[9].empty()) rmc.date_dmyt = static_cast<uint32_t>(parseInt(fields[9]));
        if (field_cnt > 12 && !fields[12].empty()) rmc.faa_mode = fields[12][0];

        return rmc;
    }

private:
    static size_t splitFields(std::string_view line, std::span<std::string_view> out) noexcept {
        size_t count = 0;
        size_t start = 0;
        for (size_t i = 0; i <= line.size() && count < out.size(); ++i) {
            if (i == line.size() || line[i] == ',') {
                out[count++] = line.substr(start, i - start);
                start = i + 1;
            }
        }
        return count;
    }

    static int hexToVal(char c) noexcept {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'A' && c <= 'F') return c - 'A' + 10;
        if (c >= 'a' && c <= 'f') return c - 'a' + 10;
        return -1;
    }

    static double parseDouble(std::string_view sv) noexcept {
        double val = 0.0;
        #if defined(__cpp_lib_to_chars) && __cpp_lib_to_chars >= 201611L
            std::from_chars(sv.data(), sv.data() + sv.size(), val);
        #else
            char tmp[32]{};
            size_t len = std::min(sv.size(), sizeof(tmp) - 1);
            sv.copy(tmp, len);
            val = std::strtod(tmp, nullptr);
        #endif
        return val;
    }

    static int parseInt(std::string_view sv) noexcept {
        int val = 0;
        std::from_chars(sv.data(), sv.data() + sv.size(), val);
        return val;
    }

    static double parseCoordinate(std::string_view sv, char hemisphere) noexcept {
        double raw = parseDouble(sv);
        int degrees = static_cast<int>(raw / 100.0);
        double minutes = raw - (degrees * 100.0);
        double deg = degrees + (minutes / 60.0);
        return (hemisphere == 'S' || hemisphere == 'W') ? -deg : deg;
    }

    State state_{State::WaitStart};
    std::array<char, 84> buffer_{};
    size_t buf_idx_{0};
    uint8_t calc_crc_{0};
    uint8_t rx_crc_{0};
    uint32_t success_{0};
    uint32_t errors_{0};
};

int main() {
    NmeaParser parser;
    std::string_view test_stream = 
        "NOISE\x1B\x00$GNGGA,123519.00,4807.0382,N,01131.0000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
        "$GNRMC,123519.00,A,4807.0382,N,01131.0000,E,022.4,084.4,230324,003.1,W,A*1D\r\n";

    for (char ch : test_stream) {
        if (auto sentence = parser.feed(static_cast<uint8_t>(ch))) {
            std::cout << "Прийнято NMEA речення: " << *sentence << "\n";
            if (auto gga = NmeaParser::parseGga(*sentence)) {
                std::cout << std::fixed << std::setprecision(6);
                std::cout << "  [GGA] Широта: " << gga->latitude << "°, Довгота: " 
                          << gga->longitude << "°, Висота: " << gga->altitude << " м\n";
            }
            if (auto rmc = NmeaParser::parseRmc(*sentence)) {
                std::cout << "  [RMC] Швидкість: " << rmc->speed_mps << " м/с, Курс: " 
                          << rmc->course_deg << "°, Валідність: " << (rmc->is_valid ? "OK" : "NO") << "\n";
            }
        }
    }

    std::cout << "\nПідсумок C++: Успішно = " << parser.successCount()
              << ", Помилок = " << parser.errorCount() << "\n";
    return 0;
}
