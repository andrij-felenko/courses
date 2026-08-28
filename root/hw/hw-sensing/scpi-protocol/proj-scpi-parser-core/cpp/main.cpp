#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <charconv>
#include <optional>
#include <expected>
#include <algorithm>
#include <cctype>

namespace embedded::scpi {

// Коди помилок згідно зі стандартом SCPI
enum class ErrorCode : int16_t {
    Ok                  = 0,
    SyntaxError         = -100,
    InvalidSeparator    = -103,
    UndefinedHeader     = -113,
    ExecutionError      = -200,
    DataOutOfRange      = -222,
    QueueOverflow       = -350,
    QueryInterrupted    = -410,
    QueryUnterminated   = -420
};

struct ErrorItem {
    ErrorCode        code{ErrorCode::Ok};
    std::string_view message{"No error"};
};

// Неблокувальний кільцевий буфер черги помилок FIFO фіксованого розміру
template <size_t Capacity = 8>
class ErrorRingBuffer {
public:
    constexpr ErrorRingBuffer() = default;

    void push(ErrorCode code, std::string_view msg) noexcept {
        if (count_ >= Capacity) {
            size_t last = (head_ == 0) ? (Capacity - 1) : (head_ - 1);
            buffer_[last] = {ErrorCode::QueueOverflow, "Queue overflow"};
            return;
        }
        buffer_[head_] = {code, msg};
        head_ = (head_ + 1) % Capacity;
        count_++;
    }

    [[nodiscard]] ErrorItem pop() noexcept {
        if (count_ == 0) {
            return {ErrorCode::Ok, "No error"};
        }
        auto item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        count_--;
        return item;
    }

    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

private:
    std::array<ErrorItem, Capacity> buffer_{};
    size_t                          head_{0};
    size_t                          tail_{0};
    size_t                          count_{0};
};

// Статичний безалокаційний потік запису відповідей
class StaticResponseBuffer {
public:
    constexpr explicit StaticResponseBuffer(std::span<char> storage) noexcept 
        : storage_(storage) {}

    void write(std::string_view text) noexcept {
        size_t available = storage_.size() - cursor_;
        size_t to_write = std::min(available, text.size());
        if (to_write > 0) {
            std::copy_n(text.data(), to_write, storage_.data() + cursor_);
            cursor_ += to_write;
        }
    }

    void write_double(double value, int precision = 4) noexcept {
        char tmp[32];
        auto [ptr, ec] = std::to_chars(tmp, tmp + sizeof(tmp), value, std::chars_format::fixed, precision);
        if (ec == std::errc()) {
            write(std::string_view(tmp, ptr - tmp));
        }
    }

    void write_int(int64_t value) noexcept {
        char tmp[32];
        auto [ptr, ec] = std::to_chars(tmp, tmp + sizeof(tmp), value);
        if (ec == std::errc()) {
            write(std::string_view(tmp, ptr - tmp));
        }
    }

    [[nodiscard]] std::string_view view() const noexcept {
        return std::string_view(storage_.data(), cursor_);
    }

    void clear() noexcept { cursor_ = 0; }

private:
    std::span<char> storage_;
    size_t          cursor_{0};
};

// Порівняння сегмента мнемоніки без урахування регістру літер
constexpr bool match_segment_token(std::string_view token, std::string_view pattern) noexcept {
    size_t short_len = 0;
    while (short_len < pattern.size() && std::isupper(static_cast<unsigned char>(pattern[short_len]))) {
        short_len++;
    }
    if (short_len == 0) short_len = pattern.size();

    auto char_match = [](char a, char b) noexcept {
        return std::toupper(static_cast<unsigned char>(a)) == std::toupper(static_cast<unsigned char>(b));
    };

    if (token.size() == short_len) {
        return std::equal(token.begin(), token.end(), pattern.begin(), pattern.begin() + short_len, char_match);
    }
    if (token.size() == pattern.size()) {
        return std::equal(token.begin(), token.end(), pattern.begin(), pattern.end(), char_match);
    }
    return false;
}

// Ієрархічне порівняння шляхів дерева
constexpr bool match_hierarchical_path(std::string_view token, std::string_view pattern) noexcept {
    while (!pattern.empty() && !token.empty()) {
        if (pattern.front() == ':') {
            if (token.front() != ':') return false;
            pattern.remove_prefix(1);
            token.remove_prefix(1);
            continue;
        }

        auto p_idx = pattern.find(':');
        auto p_seg = (p_idx != std::string_view::npos) ? pattern.substr(0, p_idx) : pattern;
        pattern.remove_prefix(p_seg.size());

        auto t_idx = token.find(':');
        auto t_seg = (t_idx != std::string_view::npos) ? token.substr(0, t_idx) : token;
        token.remove_prefix(t_seg.size());

        if (!match_segment_token(t_seg, p_seg)) return false;
    }
    return pattern.empty() && token.empty();
}

// Швидкісний числовий парсер із підтримкою суфіксів масштабування
inline std::optional<double> parse_scpi_number(std::string_view text) noexcept {
    while (!text.empty() && std::isspace(static_cast<unsigned char>(text.front()))) {
        text.remove_prefix(1);
    }
    if (text.empty()) return std::nullopt;

    double result = 0.0;
    auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), result);
    if (ec != std::errc()) return std::nullopt;

    std::string_view suffix(ptr, (text.data() + text.size()) - ptr);
    while (!suffix.empty() && std::isspace(static_cast<unsigned char>(suffix.front()))) {
        suffix.remove_prefix(1);
    }

    if (!suffix.empty()) {
        if (match_segment_token(suffix, "KV") || match_segment_token(suffix, "KHZ") || match_segment_token(suffix, "KOHM")) {
            result *= 1e3;
        } else if (match_segment_token(suffix, "MV") || match_segment_token(suffix, "MA") || match_segment_token(suffix, "MS")) {
            result *= 1e-3;
        } else if (match_segment_token(suffix, "UV") || match_segment_token(suffix, "UA") || match_segment_token(suffix, "US")) {
            result *= 1e-6;
        } else if (match_segment_token(suffix, "NV") || match_segment_token(suffix, "NA") || match_segment_token(suffix, "NS")) {
            result *= 1e-9;
        } else if (match_segment_token(suffix, "MHZ") || match_segment_token(suffix, "MOHM")) {
            result *= 1e6;
        }
    }
    return result;
}

template <typename ContextType>
struct StaticCommandEntry {
    std::string_view pattern;
    bool             is_query;
    ErrorCode (*handler)(ContextType& ctx, std::string_view args, StaticResponseBuffer& out);
};

// Головний диспетчер команд
template <typename ContextType, size_t TableSize>
class ScpiDispatcher {
public:
    constexpr explicit ScpiDispatcher(const std::array<StaticCommandEntry<ContextType>, TableSize>& table) noexcept 
        : table_(table) {}

    void execute_line(ContextType& ctx, std::string_view line, StaticResponseBuffer& response, ErrorRingBuffer<>& error_queue) const noexcept {
        while (!line.empty() && std::isspace(static_cast<unsigned char>(line.front()))) {
            line.remove_prefix(1);
        }
        if (line.empty()) return;

        response.clear();

        auto space_pos = line.find(' ');
        auto header = (space_pos != std::string_view::npos) ? line.substr(0, space_pos) : line;
        auto args = (space_pos != std::string_view::npos) ? line.substr(space_pos + 1) : std::string_view{};

        while (!args.empty() && std::isspace(static_cast<unsigned char>(args.front()))) {
            args.remove_prefix(1);
        }

        bool is_query = header.ends_with('?');
        auto match_hdr = is_query ? header.substr(0, header.size() - 1) : header;

        for (const auto& entry : table_) {
            if (entry.is_query == is_query && match_hierarchical_path(match_hdr, entry.pattern)) {
                if (auto err = entry.handler(ctx, args, response); err != ErrorCode::Ok) {
                    error_queue.push(err, "Execution error");
                }
                if (!response.view().empty()) {
                    response.write("\n");
                }
                return;
            }
        }
        error_queue.push(ErrorCode::UndefinedHeader, "Undefined header");
    }

private:
    const std::array<StaticCommandEntry<ContextType>, TableSize>& table_;
};

} // namespace embedded::scpi

// Апаратний контекст приладу (Джерело живлення)
struct HardwarePowerSupply {
    double voltage{0.0};
    double current_limit{1.0};
    bool   output_enabled{false};
    embedded::scpi::ErrorRingBuffer<8> error_queue{};
};

using PSUCommand = embedded::scpi::StaticCommandEntry<HardwarePowerSupply>;

// Compile-time таблиця диспетчеризації команд
constexpr std::array g_psu_command_map = {
    PSUCommand{"*IDN", true, [](HardwarePowerSupply&, std::string_view, embedded::scpi::StaticResponseBuffer& out) {
        out.write("TechLab,BenchPSU-3005,SN20264411,v3.1.0");
        return embedded::scpi::ErrorCode::Ok;
    }},
    PSUCommand{"*RST", false, [](HardwarePowerSupply& dev, std::string_view, embedded::scpi::StaticResponseBuffer&) {
        dev.voltage = 0.0;
        dev.current_limit = 1.0;
        dev.output_enabled = false;
        return embedded::scpi::ErrorCode::Ok;
    }},
    PSUCommand{":SYSTem:ERRor", true, [](HardwarePowerSupply& dev, std::string_view, embedded::scpi::StaticResponseBuffer& out) {
        auto err = dev.error_queue.pop();
        out.write_int(static_cast<int16_t>(err.code));
        out.write(",\"");
        out.write(err.message);
        out.write("\"");
        return embedded::scpi::ErrorCode::Ok;
    }},
    PSUCommand{":SOURce:VOLTage", false, [](HardwarePowerSupply& dev, std::string_view args, embedded::scpi::StaticResponseBuffer&) {
        auto val = embedded::scpi::parse_scpi_number(args);
        if (!val) return embedded::scpi::ErrorCode::SyntaxError;
        if (*val < 0.0 || *val > 30.0) return embedded::scpi::ErrorCode::DataOutOfRange;
        dev.voltage = *val;
        return embedded::scpi::ErrorCode::Ok;
    }},
    PSUCommand{":SOURce:VOLTage", true, [](HardwarePowerSupply& dev, std::string_view, embedded::scpi::StaticResponseBuffer& out) {
        out.write_double(dev.voltage, 4);
        return embedded::scpi::ErrorCode::Ok;
    }},
    PSUCommand{":OUTPut:STATe", false, [](HardwarePowerSupply& dev, std::string_view args, embedded::scpi::StaticResponseBuffer&) {
        if (embedded::scpi::match_segment_token(args, "ON") || args == "1") {
            dev.output_enabled = true;
        } else if (embedded::scpi::match_segment_token(args, "OFF") || args == "0") {
            dev.output_enabled = false;
        } else {
            return embedded::scpi::ErrorCode::SyntaxError;
        }
        return embedded::scpi::ErrorCode::Ok;
    }},
    PSUCommand{":OUTPut:STATe", true, [](HardwarePowerSupply& dev, std::string_view, embedded::scpi::StaticResponseBuffer& out) {
        out.write(dev.output_enabled ? "1" : "0");
        return embedded::scpi::ErrorCode::Ok;
    }}
};

int main() {
    HardwarePowerSupply psu;
    embedded::scpi::ScpiDispatcher<HardwarePowerSupply, g_psu_command_map.size()> dispatcher(g_psu_command_map);

    char tx_buffer[256];
    embedded::scpi::StaticResponseBuffer response(tx_buffer);

    std::cout << "=== Запуск тесту сучасного ядра SCPI (C++20) ===\n";

    constexpr std::array script = {
        std::string_view("*IDN?"),
        std::string_view(":SOURce:VOLTage 28.5V"),
        std::string_view(":SOUR:VOLT?"),
        std::string_view(":OUTP:STAT ON"),
        std::string_view(":OUTP:STAT?"),
        std::string_view(":SOUR:VOLT 120.0V"), // Помилка: DataOutOfRange
        std::string_view(":UNKNOWN:PATH?"),   // Помилка: UndefinedHeader
        std::string_view(":SYST:ERR?"),
        std::string_view(":SYST:ERR?"),
        std::string_view(":SYST:ERR?")
    };

    for (auto line : script) {
        std::cout << ">> " << line << "\n";
        dispatcher.execute_line(psu, line, response, psu.error_queue);
        if (!response.view().empty()) {
            std::cout << "<< " << response.view();
        }
    }

    return 0;
}
