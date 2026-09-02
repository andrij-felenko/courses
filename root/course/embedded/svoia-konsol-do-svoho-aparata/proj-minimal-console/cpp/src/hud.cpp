#include "hud.hpp"

#include <algorithm>
#include <charconv>

namespace console {
namespace {

constexpr std::size_t kGlyphWidth = 5;
constexpr std::size_t kCellWidth = 6;

// Шрифт 5×8: кожен байт — вертикальний стовпчик пікселів, молодший біт зверху.
// Гліфи лише під ті символи, що трапляються в написах пульта; кирилиці в
// такому шрифті немає, тому підписи латиницею.
constexpr std::string_view kCharset = " -.%0123456789ABCDEFGHIKLMNOPQRSTUVY";

constexpr std::array<std::array<std::uint8_t, kGlyphWidth>, 36> kFont{{
    {0x00, 0x00, 0x00, 0x00, 0x00},   // пробіл
    {0x08, 0x08, 0x08, 0x08, 0x08},   // -
    {0x00, 0x60, 0x60, 0x00, 0x00},   // .
    {0x23, 0x13, 0x08, 0x64, 0x62},   // %
    {0x3E, 0x51, 0x49, 0x45, 0x3E},   // 0
    {0x00, 0x42, 0x7F, 0x40, 0x00},   // 1
    {0x42, 0x61, 0x51, 0x49, 0x46},   // 2
    {0x21, 0x41, 0x45, 0x4B, 0x31},   // 3
    {0x18, 0x14, 0x12, 0x7F, 0x10},   // 4
    {0x27, 0x45, 0x45, 0x45, 0x39},   // 5
    {0x3C, 0x4A, 0x49, 0x49, 0x30},   // 6
    {0x01, 0x71, 0x09, 0x05, 0x03},   // 7
    {0x36, 0x49, 0x49, 0x49, 0x36},   // 8
    {0x06, 0x49, 0x49, 0x29, 0x1E},   // 9
    {0x7E, 0x11, 0x11, 0x11, 0x7E},   // A
    {0x7F, 0x49, 0x49, 0x49, 0x36},   // B
    {0x3E, 0x41, 0x41, 0x41, 0x22},   // C
    {0x7F, 0x41, 0x41, 0x22, 0x1C},   // D
    {0x7F, 0x49, 0x49, 0x49, 0x41},   // E
    {0x7F, 0x09, 0x09, 0x09, 0x01},   // F
    {0x3E, 0x41, 0x49, 0x49, 0x7A},   // G
    {0x7F, 0x08, 0x08, 0x08, 0x7F},   // H
    {0x00, 0x41, 0x7F, 0x41, 0x00},   // I
    {0x7F, 0x08, 0x14, 0x22, 0x41},   // K
    {0x7F, 0x40, 0x40, 0x40, 0x40},   // L
    {0x7F, 0x02, 0x0C, 0x02, 0x7F},   // M
    {0x7F, 0x04, 0x08, 0x10, 0x7F},   // N
    {0x3E, 0x41, 0x41, 0x41, 0x3E},   // O
    {0x7F, 0x09, 0x09, 0x09, 0x06},   // P
    {0x3E, 0x41, 0x51, 0x21, 0x5E},   // Q
    {0x7F, 0x09, 0x19, 0x29, 0x46},   // R
    {0x46, 0x49, 0x49, 0x49, 0x31},   // S
    {0x01, 0x01, 0x7F, 0x01, 0x01},   // T
    {0x3F, 0x40, 0x40, 0x40, 0x3F},   // U
    {0x1F, 0x20, 0x40, 0x20, 0x1F},   // V
    {0x07, 0x08, 0x70, 0x08, 0x07},   // Y
}};

[[nodiscard]] constexpr std::span<const std::uint8_t, kGlyphWidth> glyph(char symbol) noexcept
{
    const auto index = kCharset.find(symbol);
    return kFont[index == std::string_view::npos ? 0 : index];
}

}   // namespace

void TextLine::append(char symbol) noexcept
{
    if (used_ < buffer_.size()) {
        buffer_[used_++] = symbol;
    }
}

void TextLine::append(std::string_view text) noexcept
{
    const auto room = std::min(text.size(), buffer_.size() - used_);
    std::ranges::copy(text.substr(0, room), buffer_.begin() + static_cast<std::ptrdiff_t>(used_));
    used_ += room;
}

void TextLine::appendNumber(std::uint32_t value, int minDigits) noexcept
{
    std::array<char, 10> digits{};
    const auto result = std::to_chars(digits.data(), digits.data() + digits.size(), value);
    const auto written = static_cast<int>(result.ptr - digits.data());
    for (int i = written; i < minDigits; ++i) {
        append('0');
    }
    append(std::string_view{digits.data(), static_cast<std::size_t>(written)});
}

void TextLine::appendMillivolts(std::uint16_t millivolts) noexcept
{
    appendNumber(millivolts / 1000u);
    append('.');
    appendNumber((millivolts % 1000u) / 10u, 2);
}

void Hud::buildLine(std::uint8_t page, TextLine& line) const noexcept
{
    line.clear();
    switch (page) {
    case 0:
        line.append("BAT ");
        line.appendMillivolts(snapshot_.packMillivolts);
        line.append("V ");
        line.append(snapshot_.batteryLevel == BatteryMonitor::Level::Critical ? "KRYT"
                    : snapshot_.batteryLevel == BatteryMonitor::Level::Low    ? "MALO"
                                                                             : "OK");
        break;
    case 1:
        line.append("LQ ");
        line.appendNumber(snapshot_.linkQuality, 3);
        line.append("% RSSI -");
        line.appendNumber(static_cast<std::uint32_t>(-snapshot_.air.rssiDbm), 3);
        break;
    case 2:
        line.append("APARAT ");
        line.appendMillivolts(snapshot_.air.vbatMv);
        line.append('V');
        break;
    case 3:
        line.append("STRUM ");
        line.appendNumber(snapshot_.air.currentDeciAmp / 10u);
        line.append('.');
        line.appendNumber(snapshot_.air.currentDeciAmp % 10u);
        line.append('A');
        break;
    case 4:
        line.append("MOS ");
        line.appendNumber(snapshot_.air.mosTempC, 2);
        line.append("C SAT ");
        line.appendNumber(snapshot_.air.satellites, 2);
        break;
    case 6:
        line.append("MOD ");
        line.appendNumber(snapshot_.air.flightMode, 2);
        line.append(snapshot_.armed ? " ARM" : " SAFE");
        break;
    case 7:
        // Найважливіший рядок: чому передачі немає. Він же й найнижчий, бо
        // саме туди падає погляд, коли апарат не реагує.
        if (snapshot_.faults & Fault::AxisDead) {
            line.append("BLOK DATCHYK");
        } else if (snapshot_.faults & Fault::ThrottleUp) {
            line.append("BLOK TAHA");
        } else if (snapshot_.faults & Fault::ArmEngaged) {
            line.append("BLOK ARM");
        } else {
            line.append("VTRATY ");
            line.appendNumber(snapshot_.lostFrames, 4);
        }
        break;
    default:
        break;
    }
}

void Hud::renderText(std::string_view text) noexcept
{
    columns_.fill(std::byte{0});
    std::size_t x = 0;
    for (char symbol : text) {
        if (x + kCellWidth > columns_.size()) {
            break;
        }
        const auto bitmap = glyph(symbol);
        for (std::size_t i = 0; i < kGlyphWidth; ++i) {
            columns_[x + i] = static_cast<std::byte>(bitmap[i]);
        }
        x += kCellWidth;
    }
}

void Hud::renderBar(std::uint8_t percent) noexcept
{
    columns_.fill(std::byte{0});
    const std::size_t fill = static_cast<std::size_t>(percent) * (columns_.size() - 2) / 100;
    columns_.front() = std::byte{0x7E};
    columns_.back() = std::byte{0x7E};
    for (std::size_t x = 1; x + 1 < columns_.size(); ++x) {
        columns_[x] = (x <= fill) ? std::byte{0x7E} : std::byte{0x42};   // залито або рамка
    }
}

void Hud::servicePage() noexcept
{
    if (page_ == 5) {
        renderBar(snapshot_.linkQuality);
    } else {
        TextLine line{};
        buildLine(page_, line);
        renderText(line.view());
    }

    // Дисплей висить на тій самій шині SPI, що й трансивер: сюди ми
    // потрапляємо лише тоді, коли радіо шину не тримає.
    hal::displayPage(page_, columns_);
    page_ = static_cast<std::uint8_t>((page_ + 1) & 7);
}

}   // namespace console
