#include "rack_lines.hpp"

#include <cstdio>
#include <format>
#include <stdexcept>

#include <fcntl.h>
#include <linux/gpio.h>
#include <sys/ioctl.h>

namespace {

// Релейна плата слота — розширювач на I2C, який ядро реєструє власним gpiochip,
// тож udev дає симлінк на кожен слот, а зміщення всередині чипа фіксовані.
constexpr std::uint32_t kLineVcc = 0;
constexpr std::uint32_t kLineBoot0 = 1;

constexpr std::uint64_t kBitVcc = 1ULL << kLineVcc;
constexpr std::uint64_t kBitBoot0 = 1ULL << kLineBoot0;

} // namespace

RackLines::RackLines(int slotId)
{
    const auto path = std::format("/dev/dut-slot-{:02d}-pwr", slotId);

    UniqueFd chip{::open(path.c_str(), O_RDWR | O_CLOEXEC)};
    if (!chip) {
        throwErrno(std::format("не відкривається {}", path));
    }

    gpio_v2_line_request req{};
    req.offsets[0] = kLineVcc;
    req.offsets[1] = kLineBoot0;
    req.num_lines = 2;
    std::snprintf(req.consumer, sizeof req.consumer, "rack-slot-%02d", slotId);
    req.config.flags = GPIO_V2_LINE_FLAG_OUTPUT;

    // Початкові рівні їдуть тим самим запитом: лінії стають виходами вже з нулем.
    // Інакше між зміною напрямку і першим записом плата ловить імпульс живлення.
    req.config.num_attrs = 1;
    req.config.attrs[0].attr.id = GPIO_V2_LINE_ATTR_ID_OUTPUT_VALUES;
    req.config.attrs[0].attr.values = 0;
    req.config.attrs[0].mask = kBitVcc | kBitBoot0;

    if (::ioctl(chip.get(), GPIO_V2_GET_LINE_IOCTL, &req) < 0) {
        throwErrno(std::format("GPIO_V2_GET_LINE на слоті {:02d}", slotId));
    }

    // Далі чип не потрібен: лінії тримає саме дескриптор запиту.
    lines_.reset(req.fd);
}

void RackLines::setLines(std::uint64_t mask, std::uint64_t bits)
{
    if (!lines_) {
        throw std::runtime_error{"спроба керувати живленням незахопленого слота"};
    }

    gpio_v2_line_values values{};
    values.mask = mask; // чіпаємо лише названі лінії, друга лишається як була
    values.bits = bits;

    if (::ioctl(lines_.get(), GPIO_V2_LINE_SET_VALUES_IOCTL, &values) < 0) {
        throwErrno("GPIO_V2_LINE_SET_VALUES");
    }
}

void RackLines::vcc(bool on)
{
    setLines(kBitVcc, on ? kBitVcc : 0);
}

void RackLines::boot0(bool high)
{
    setLines(kBitBoot0, high ? kBitBoot0 : 0);
}

void RackLines::shutdownQuietly() noexcept
{
    if (!lines_) {
        return;
    }
    // Знеструмлюємо ДО звільнення ліній: після нього стан виходів визначає
    // драйвер розширювача, а не ми, і слот міг би лишитися під напругою.
    try {
        setLines(kBitVcc | kBitBoot0, 0);
    } catch (...) {
        // Деструктор не має права кидати, а слот усе одно віддаємо.
    }
    lines_.reset();
}
