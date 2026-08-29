// telemetry.hpp — складання діагностичного рядка й діагностичний порт.
//
// Ані переривань, ані DMA, ані кільцевого буфера: цей канал мусить
// працювати в аварійній гілці, коли решті системи вже не довіряють.
#pragma once

#include "crash_report.hpp"

#include <cstdint>
#include <span>
#include <string_view>

namespace diag {

// Складач рядка поверх чужого буфера. Пам'яті не виділяє й не володіє нею:
// у гілці аварії стек уже може бути зіпсований, а купи в прошивці немає
// взагалі. Переповнення не обрізає мовчки — про нього видно з truncated().
class LineBuilder {
public:
    explicit constexpr LineBuilder(std::span<char> buffer) noexcept : buf_{buffer} {}

    LineBuilder& operator<<(std::string_view text) noexcept;
    LineBuilder& operator<<(std::uint32_t value) noexcept;

    // Шістнадцяткове з префіксом 0x і повними вісьмома цифрами:
    // адреси зручно читати, коли вони однакової ширини.
    LineBuilder& hex(std::uint32_t value) noexcept;

    [[nodiscard]] std::string_view view() const noexcept { return {buf_.data(), len_}; }
    [[nodiscard]] bool truncated() const noexcept { return truncated_; }

private:
    [[nodiscard]] std::size_t room() const noexcept { return buf_.size() - len_; }

    std::span<char> buf_;
    std::size_t len_{0};
    bool truncated_{false};
};

class Telemetry {
public:
    Telemetry() = delete;

    static void init() noexcept;

    // Друк опитуванням із запобіжником на випадок мертвого передавача:
    // зависнути на очікуванні TXE у виробі не можна.
    static void write(std::string_view text) noexcept;
    static void line(std::string_view text) noexcept;

    // Рядок телеметрії у наданий буфер. Повертає представлення тієї
    // частини буфера, яку справді заповнено.
    [[nodiscard]] static std::string_view render(const CrashReport& report,
                                                 std::span<char> scratch) noexcept;
};

} // namespace diag
