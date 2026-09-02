#include "i2c_mux.hpp"

namespace board {
namespace {
/* Даташит вимагає імпульсу ~RESET від 6 нс; 1 мкс — із запасом. */
constexpr std::uint32_t kResetPulseUs = 1;
}  // namespace

Tca9548a::Tca9548a(I2cBus& bus, std::uint8_t address, GpioPort* gpio,
                   std::uint8_t resetPin)
    : bus_(bus), gpio_(gpio), address_(address), resetPin_(resetPin) {}

Result<void> Tca9548a::writeControl(std::uint8_t mask) {
    const std::uint8_t frame[]{mask};
    auto r = bus_.write(address_, frame);
    if (r) {
        shadow_ = mask;
        shadowValid_ = true;
    } else {
        /* Невідомо, чи засвоїв комутатор байт до зриву транзакції —
           тінь більше не дійсна, наступний виклик піде наосліп. */
        shadowValid_ = false;
    }
    return r;
}

void Tca9548a::hardReset() {
    if (gpio_ == nullptr || resetPin_ == kNoPin) {
        return;
    }
    gpio_->write(resetPin_, false);
    gpio_->delayUs(kResetPulseUs);
    gpio_->write(resetPin_, true);
    gpio_->delayUs(kResetPulseUs);

    shadow_ = kAllOff;
    shadowValid_ = true;  /* після скидання всі ключі гарантовано розімкнені */
}

Result<void> Tca9548a::begin() {
    if (address_ < kBaseAddress ||
        address_ > static_cast<std::uint8_t>(kBaseAddress + 7)) {
        return std::unexpected(BusError::Argument);
    }
    /* Живлення могло й не зникати: теплий перезапуск мікроконтролера лишає
       комутатор із відкритим каналом і чужим давачем на головній шині. */
    hardReset();
    return isolate();
}

Result<void> Tca9548a::isolate() {
    if (shadowValid_ && shadow_ == kAllOff) {
        return {};
    }
    auto r = writeControl(kAllOff);
    if (!r) {
        /* Лишити невідомо які ключі замкненими не можна: обмін піде відразу
           з двома субшинами. Скидання ізолює напевно, але помилку віддаємо
           нагору — шина щойно збоїла, і про це має знати логіка вище. */
        hardReset();
    }
    return r;
}

Result<Tca9548a::Channel> Tca9548a::open(std::uint8_t channel) {
    if (channel >= kChannels) {
        return std::unexpected(BusError::Argument);
    }
    const auto mask = static_cast<std::uint8_t>(1u << channel);

    if (!(shadowValid_ && shadow_ == mask)) {
        auto r = writeControl(mask);
        if (!r) {
            /* Комутатор міг зависнути із замкненими ключами й тримати
               ємність усіх субшин на головній лінії — б'ємо ~RESET. */
            hardReset();
            auto again = writeControl(mask);
            if (!again) {
                return std::unexpected(again.error());
            }
        }
    }
    return Channel{*this, channel};
}

Result<std::uint8_t> Tca9548a::controlByte() {
    /* Читання самого комутатора повертає його регістр керування — так
       перевіряють, що ключі справді там, куди ми їх поставили. */
    std::uint8_t value{};
    if (auto r = bus_.read(address_, std::span{&value, 1}); !r) {
        return std::unexpected(r.error());
    }
    return value;
}

Tca9548a::Channel::Channel(Channel&& other) noexcept
    : mux_(other.mux_), index_(other.index_) {
    other.mux_ = nullptr;  /* власність на відкритий канал переїхала */
}

Tca9548a::Channel::~Channel() {
    if (mux_ != nullptr) {
        /* Помилку ізоляції тут нікому віддавати; вона вже осіла в тіні
           комутатора, і наступний open() почне з апаратного скидання. */
        static_cast<void>(mux_->isolate());
    }
}

Result<Tca9548a::Channel> MuxBank::open(std::uint8_t subbus) {
    const std::size_t index = subbus / Tca9548a::kChannels;
    const auto channel = static_cast<std::uint8_t>(subbus % Tca9548a::kChannels);
    if (index >= muxes_.size()) {
        return std::unexpected(BusError::Argument);
    }

    /* Спершу гасимо решту комутаторів: два відкриті канали злили б дві
       субшини в одну — разом з їхніми однаковими адресами й ємністю. */
    for (std::size_t i = 0; i < muxes_.size(); ++i) {
        if (i == index) {
            continue;
        }
        if (auto r = muxes_[i].isolate(); !r) {
            return std::unexpected(r.error());
        }
    }
    return muxes_[index].open(channel);
}

Result<void> MuxBank::isolateAll() {
    Result<void> first{};
    for (auto& mux : muxes_) {
        if (auto r = mux.isolate(); !r && first) {
            first = std::unexpected(r.error());  /* гасимо решту попри збій */
        }
    }
    return first;
}

MuxBank::PollResult MuxBank::poll(std::uint8_t device, std::uint8_t reg,
                                  std::span<std::uint8_t> out,
                                  std::uint8_t len) {
    const std::size_t total = subbusCount();
    if (len == 0 || total == 0 || out.size() < total * len) {
        return PollResult{0, ~std::uint64_t{0}};
    }

    PollResult result{0, 0};
    const std::uint8_t command[]{reg};

    for (std::size_t sb = 0; sb < total; ++sb) {
        const std::uint64_t bit = std::uint64_t{1} << sb;
        auto channel = open(static_cast<std::uint8_t>(sb));
        if (!channel) {
            result.failed |= bit;
            continue;
        }

        auto slot = out.subspan(sb * len, len);
        if (auto r = muxes_[sb / Tca9548a::kChannels].bus()
                         .writeRead(device, command, slot);
            !r) {
            /* Мертвий давач не зупиняє обхід: реєстратор мусить зібрати
               решту зон, а зламану лише позначити бітом у масці. */
            result.failed |= bit;
            continue;
        }
        ++result.ok;
        /* Канал зачиняє деструктор channel наприкінці ітерації. */
    }

    static_cast<void>(isolateAll());
    return result;
}

}  // namespace board
