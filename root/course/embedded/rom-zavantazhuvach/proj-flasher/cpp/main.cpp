#include "bootloader.hpp"
#include "serial_port.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <format>
#include <fstream>
#include <iostream>
#include <optional>
#include <span>
#include <stdexcept>
#include <string_view>
#include <type_traits>
#include <vector>

namespace {

// Регістр розміру Flash у KiB лежить у різних родин за різними адресами,
// тому таблиця зв'язує PID із конкретною адресою й людською назвою.
struct ChipInfo {
    std::uint16_t pid;
    std::string_view name;
    std::uint32_t flashSizeReg;
};

constexpr std::array kKnownChips{
    ChipInfo{0x410, "STM32F10x medium-density", 0x1FFFF7E0u},
    ChipInfo{0x412, "STM32F10x low-density", 0x1FFFF7E0u},
    ChipInfo{0x414, "STM32F10x high-density", 0x1FFFF7E0u},
    ChipInfo{0x413, "STM32F405/407/415/417", 0x1FFF7A22u},
    ChipInfo{0x419, "STM32F42x/43x", 0x1FFF7A22u},
    ChipInfo{0x431, "STM32F411", 0x1FFF7A22u},
    ChipInfo{0x440, "STM32F05x", 0x1FFFF7CCu},
    ChipInfo{0x444, "STM32F03x", 0x1FFFF7CCu},
    ChipInfo{0x415, "STM32L47x/48x", 0x1FFF75E0u},
    ChipInfo{0x460, "STM32G07x/08x", 0x1FFF75E0u},
    ChipInfo{0x466, "STM32G03x/04x", 0x1FFF75E0u},
    ChipInfo{0x468, "STM32G43x/44x", 0x1FFF75E0u},
};

const ChipInfo* findChip(std::uint16_t pid)
{
    const auto it = std::ranges::find(kKnownChips, pid, &ChipInfo::pid);
    return it == kKnownChips.end() ? nullptr : &*it;
}

// Розгортає Result або перетворює код помилки на виняток із назвою кроку.
template <class T>
T unwrap(Result<T>&& result, std::string_view step)
{
    if (!result) {
        throw std::runtime_error(std::format("{}: {}", step, describe(result.error())));
    }
    if constexpr (!std::is_void_v<T>) {
        return std::move(*result);
    }
}

// Читає .bin і доповнює хвіст 0xFF до межі подвійного слова: на кристалах
// з ECC у Flash невирівняний запис просто не пройде.
std::vector<std::uint8_t> loadFirmware(const std::filesystem::path& path)
{
    std::ifstream file{path, std::ios::binary};
    if (!file) {
        throw std::runtime_error(std::format("не відкривається {}", path.string()));
    }

    std::vector<std::uint8_t> image{std::istreambuf_iterator<char>{file},
                                    std::istreambuf_iterator<char>{}};
    if (file.bad()) {
        throw std::runtime_error(std::format("обірване читання {}", path.string()));
    }
    if (image.empty()) {
        throw std::runtime_error("порожній образ");
    }

    const std::size_t padded = (image.size() + 7) & ~std::size_t{7};
    if (padded != image.size()) {
        std::cout << std::format("образ доповнено з {} до {} байтів (вирівнювання під ECC)\n",
                                 image.size(), padded);
        image.resize(padded, 0xFF);
    }
    return image;
}

std::uint32_t readWordLe(std::span<const std::uint8_t> data)
{
    return static_cast<std::uint32_t>(data[0]) | (static_cast<std::uint32_t>(data[1]) << 8) |
           (static_cast<std::uint32_t>(data[2]) << 16) | (static_cast<std::uint32_t>(data[3]) << 24);
}

// Дешева перевірка, що це саме прошивка, а не .elf чи чужий файл: слово 0 —
// початковий стек у SRAM, слово 1 — Reset_Handler у Flash із бітом Thumb.
void validateVectors(std::span<const std::uint8_t> image)
{
    if (image.size() < 8) {
        throw std::runtime_error("образ коротший за таблицю векторів");
    }

    const std::uint32_t stackTop = readWordLe(image.first(4));
    const std::uint32_t resetVector = readWordLe(image.subspan(4, 4));

    if ((stackTop & 0xFFF00000u) != 0x20000000u) {
        throw std::runtime_error(
            std::format("слово 0 = {:#010x} — це не вершина стека в SRAM", stackTop));
    }
    if ((resetVector & 1u) == 0 || resetVector < kFlashBase ||
        resetVector >= kFlashBase + image.size()) {
        throw std::runtime_error(
            std::format("слово 1 = {:#010x} — Reset_Handler поза образом", resetVector));
    }
}

void writeImage(Bootloader& boot, std::span<const std::uint8_t> image)
{
    for (std::size_t offset = 0; offset < image.size(); offset += kMaxBlock) {
        const auto chunk = image.subspan(offset, std::min(kMaxBlock, image.size() - offset));
        const auto address = static_cast<std::uint32_t>(kFlashBase + offset);

        unwrap(boot.writeBlock(address, chunk), std::format("запис на {:#010x}", address));

        std::cout << std::format("\r  запис {:#010x}  {:3}%", address,
                                 (offset + chunk.size()) * 100 / image.size())
                  << std::flush;
    }
    std::cout << '\n';
}

void verifyImage(Bootloader& boot, std::span<const std::uint8_t> image)
{
    for (std::size_t offset = 0; offset < image.size(); offset += kMaxBlock) {
        const auto expected = image.subspan(offset, std::min(kMaxBlock, image.size() - offset));
        const auto address = static_cast<std::uint32_t>(kFlashBase + offset);

        const auto actual =
            unwrap(boot.readBlock(address, expected.size()), std::format("читання {:#010x}", address));

        const auto mismatch = std::ranges::mismatch(actual, expected);
        if (mismatch.in1 != actual.end()) {
            const auto at = static_cast<std::size_t>(mismatch.in1 - actual.begin());
            throw std::runtime_error(
                std::format("розбіжність на {:#010x}: у чипі {:#04x}, в образі {:#04x}",
                            address + at, *mismatch.in1, *mismatch.in2));
        }

        std::cout << std::format("\r  звірка {:#010x}  {:3}%", address,
                                 (offset + expected.size()) * 100 / image.size())
                  << std::flush;
    }
    std::cout << '\n';
}

void flash(const std::string& portPath, std::span<const std::uint8_t> image)
{
    SerialPort port{portPath};
    port.enterBootloader();

    Bootloader boot{port};
    unwrap(boot.sync(), "синхронізація (перевір BOOT0 і перехідник)");

    const auto version = unwrap(boot.version(), "Get Version");
    std::cout << std::format("завантажувач версії {}.{}\n", version.protocol >> 4,
                             version.protocol & 0x0F);

    const auto pid = unwrap(boot.chipId(), "Get ID");
    const ChipInfo* chip = findChip(pid);
    if (chip == nullptr) {
        throw std::runtime_error(
            std::format("PID {:#05x} у таблиці відсутній — адреса регістра розміру невідома", pid));
    }
    std::cout << std::format("кристал {:#05x} — {}\n", pid, chip->name);

    // Пробне читання водночас перевіряє захист: під RDP level 1 буде NACK.
    auto sizeBytes = boot.readBlock(chip->flashSizeReg, 2);
    bool erasedByUnprotect = false;

    if (!sizeBytes && sizeBytes.error() == BootError::Nack) {
        std::cout << "читання заблоковано — RDP level 1; знімаємо захист, Flash буде стерто\n";
        unwrap(boot.readoutUnprotect(), "Readout Unprotect");

        // Чип сам перезавантажився — заходимо в System Memory ще раз.
        port.enterBootloader();
        unwrap(boot.sync(), "повторна синхронізація");

        sizeBytes = boot.readBlock(chip->flashSizeReg, 2);
        erasedByUnprotect = true;
    }

    const auto raw = unwrap(std::move(sizeBytes), "читання розміру Flash");
    const auto flashKib = static_cast<std::uint16_t>(raw[0] | (raw[1] << 8));
    if (flashKib == 0 || flashKib == 0xFFFF) {
        throw std::runtime_error(
            std::format("регістр розміру віддав {:#06x} — довіряти йому не можна", flashKib));
    }
    std::cout << std::format("Flash {} KiB, образ {} байтів\n", flashKib, image.size());

    if (image.size() > static_cast<std::size_t>(flashKib) * 1024) {
        throw std::runtime_error("образ не влазить у Flash");
    }

    if (erasedByUnprotect) {
        std::cout << "стирання вже зроблено зняттям захисту\n";
    } else {
        std::cout << "масове стирання (до 30 с)...\n";
        unwrap(boot.massErase(), "Extended Erase");
    }

    writeImage(boot, image);
    verifyImage(boot, image);

    if (auto jump = boot.go(kFlashBase); !jump) {
        throw std::runtime_error(std::format("Go: {} (прошивка записана, потрібне ручне скидання)",
                                             describe(jump.error())));
    }
    std::cout << std::format("готово: керування передано на {:#010x}\n", kFlashBase);
}

} // namespace

int main(int argc, char** argv)
{
    const std::span<char*> args{argv, static_cast<std::size_t>(argc)};
    if (args.size() != 3) {
        std::cerr << std::format("вжиток: {} <порт> <прошивка.bin>\n", args[0]);
        return 2;
    }

    try {
        const auto image = loadFirmware(args[2]);
        validateVectors(image);
        flash(args[1], image);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
