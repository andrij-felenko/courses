#include "io_expander.hpp"

namespace board {
namespace {

/* Мапа регістрів при IOCON.BANK = 0 */
constexpr std::uint8_t kIodirA = 0x00;
constexpr std::uint8_t kIodirB = 0x01;
constexpr std::uint8_t kIpolA = 0x02;
constexpr std::uint8_t kGpintenA = 0x04;
constexpr std::uint8_t kIoconBank1 = 0x05;
constexpr std::uint8_t kIntconA = 0x08;
constexpr std::uint8_t kIocon = 0x0A;
constexpr std::uint8_t kGppuA = 0x0C;
constexpr std::uint8_t kIntfA = 0x0E;
constexpr std::uint8_t kIntcapA = 0x10;
constexpr std::uint8_t kGpioA = 0x12;
constexpr std::uint8_t kOlatB = 0x15;

/* Біти IOCON */
constexpr std::uint8_t kIoconMirror = 0x40;  /* INTA і INTB — один сигнал */
constexpr std::uint8_t kIoconOdr = 0x04;     /* INT з відкритим стоком */

}  // namespace

Result<void> Mcp23017::begin() {
    if (cfg_.address < kBaseAddress ||
        cfg_.address > static_cast<std::uint8_t>(kBaseAddress + 7)) {
        return std::unexpected(BusError::Argument);
    }

    struct RegisterWrite {
        std::uint8_t reg;
        std::uint8_t value;
    };

    const RegisterWrite sequence[]{
        /* Чип міг лишитися в мапі BANK = 1 після теплого перезапуску МК.
           Нуль за адресою 0x05 повертає його в BANK = 0, бо в тій мапі 0x05
           і є IOCON. Якщо ж він уже в BANK = 0, ми записали нуль у GPINTENB:
           порт B у нас під реле, переривань звідти однаково не треба. */
        {kIoconBank1, 0x00},
        {kIocon, kIoconMirror | kIoconOdr},
        {kIodirA, cfg_.inputs},
        {kGppuA, cfg_.pullups},
        {kIpolA, cfg_.inverted},
        /* INTCON = 0 — переривання за зміною рівня, а не за розбіжністю з
           еталоном DEFVAL: кінцевик цікавить нас в обидва боки. */
        {kIntconA, 0x00},
        {kGpintenA, static_cast<std::uint8_t>(cfg_.interrupts & cfg_.inputs)},
        /* Порт B — вісім виходів реле, усі знеструмлені на старті. */
        {kIodirB, 0x00},
        {kOlatB, 0x00},
    };

    for (const auto& [reg, value] : sequence) {
        if (auto r = bus_.writeRegister(cfg_.address, reg, value); !r) {
            return std::unexpected(r.error());
        }
    }
    relayShadow_ = 0;

    /* Налаштування смикало входи — прапорець уже міг звестися, а разом з ним
       і лінія INT. Знімаємо його читанням INTCAP. */
    if (auto r = bus_.readRegister(cfg_.address, kIntcapA); !r) {
        return std::unexpected(r.error());
    }
    return {};
}

Result<void> Mcp23017::setRelays(std::uint8_t mask) {
    if (auto r = bus_.writeRegister(cfg_.address, kOlatB, mask); !r) {
        return std::unexpected(r.error());
    }
    relayShadow_ = mask;
    return {};
}

Result<void> Mcp23017::setRelay(std::uint8_t index, bool on) {
    if (index > 7) {
        return std::unexpected(BusError::Argument);
    }

    /* Тіньова копія рятує від читання-модифікації-запису через шину: саме
       лише читання OLAT коштувало б іще 30 мкс, а стан виходів усе одно
       ніхто, крім мікроконтролера, не міняє. */
    const auto bit = static_cast<std::uint8_t>(1u << index);
    const auto mask = static_cast<std::uint8_t>(on ? (relayShadow_ | bit)
                                                   : (relayShadow_ & ~bit));
    if (mask == relayShadow_) {
        return {};
    }
    return setRelays(mask);
}

Result<std::uint8_t> Mcp23017::inputs() {
    return bus_.readRegister(cfg_.address, kGpioA);
}

Result<std::optional<Mcp23017::Event>> Mcp23017::takeEvent() {
    auto flags = bus_.readRegister(cfg_.address, kIntfA);
    if (!flags) {
        return std::unexpected(flags.error());
    }
    if (*flags == 0) {
        return std::optional<Event>{};  /* лінію тримав не цей чип */
    }

    /* Читаємо саме INTCAP, а не GPIO. У INTCAP лежить зліпок входів на
       мікросекунду перепаду: кнопка вже могла відскочити, і GPIO показав би
       спокій — подія загубилася б. Це ж читання відпускає лінію INT. */
    auto captured = bus_.readRegister(cfg_.address, kIntcapA);
    if (!captured) {
        return std::unexpected(captured.error());
    }
    return std::optional<Event>{Event{cfg_.address, *flags, *captured}};
}

Result<std::size_t> ExpanderBank::service(std::span<Mcp23017::Event> out) {
    std::size_t count = 0;
    std::optional<BusError> firstError;

    /* Виходи INT з відкритим стоком зведені разом: поки хоч один чип тримає
       лінію в нулі, спадного фронту на вході EXTI більше не буде. Тому
       обходимо ВЕСЬ банк — і повторюємо, доки підтяжка не підніме лінію. */
    for (unsigned pass = 0; pending(); ++pass) {
        if (pass >= kMaxPasses) {
            /* Лінія залипла: чип не відпускає її навіть після читання. */
            firstError = firstError.value_or(BusError::Bus);
            break;
        }

        bool drained = false;
        for (auto& chip : chips_) {
            auto event = chip.takeEvent();
            if (!event) {
                /* Німий чип не звільняє нас від обходу решти банку. */
                firstError = firstError.value_or(event.error());
                continue;
            }
            if (!event->has_value()) {
                continue;
            }

            drained = true;
            if (count < out.size()) {
                out[count++] = **event;
            }
            /* Переповнення буфера не страшне: прапорці ми вже зняли, а
               зафіксований стан входів прийде з наступною подією. */
        }

        if (!drained) {
            /* Лінія в нулі, а зізнаватися нема кому: обірвана підтяжка або
               на монтажне «АБО» повішено ще щось, чого драйвер не знає. */
            firstError = firstError.value_or(BusError::Bus);
            break;
        }
    }

    if (count == 0 && firstError.has_value()) {
        return std::unexpected(*firstError);
    }
    return count;
}

}  // namespace board
