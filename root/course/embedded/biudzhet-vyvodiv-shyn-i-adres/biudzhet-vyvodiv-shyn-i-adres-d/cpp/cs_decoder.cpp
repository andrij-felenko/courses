#include "cs_decoder.hpp"

namespace board {

Hc138ChipSelect::Hc138ChipSelect(GpioPort& gpio, const Pins& pins)
    : gpio_(gpio), pins_(pins) {
    /* Найперша дія на старті — зняти дозвіл. Поки строб не піднято, а
       адресні виводи ще у скиданому стані, дешифратор тримає випадковий
       вихід у нулі, і якийсь чип уже слухає шину, якої ще не налаштовано. */
    gpio_.write(pins_.enable, true);
    gpio_.write(pins_.a0, false);
    gpio_.write(pins_.a1, false);
    gpio_.write(pins_.a2, false);
    if (pins_.a3 != kNoPin) {
        gpio_.write(pins_.a3, false);
    }
}

void Hc138ChipSelect::release() noexcept {
    gpio_.write(pins_.enable, true);
}

Result<Hc138ChipSelect::Selection> Hc138ChipSelect::select(
    std::uint8_t device) {
    if (device >= lines()) {
        return std::unexpected(BusError::Argument);
    }

    /* 1. Знімаємо дозвіл: усі виходи підіймаються в одиницю, жодного чипа
          не вибрано. Саме це вбиває гліч на лініях CS. */
    gpio_.write(pins_.enable, true);

    /* 2. Виставляємо двійковий номер. Різний час перемикання виводів МК
          тепер не важить — виходи дешифратора заблоковані. */
    gpio_.write(pins_.a0, (device & 0x01u) != 0);
    gpio_.write(pins_.a1, (device & 0x02u) != 0);
    gpio_.write(pins_.a2, (device & 0x04u) != 0);
    if (pins_.a3 != kNoPin) {
        /* Старший біт вибирає, котрий із двох каскадованих чипів дозволено. */
        gpio_.write(pins_.a3, (device & 0x08u) != 0);
    }

    /* 3. Даємо дозвіл: рівно один вихід падає в нуль за 15..20 нс. Окремої
          затримки не треба — запис у регістр SPI і так довший. */
    gpio_.write(pins_.enable, false);
    return Selection{*this, device};
}

Result<void> Hc138ChipSelect::command(SpiBus& spi, std::uint8_t device,
                                      std::span<const std::uint8_t> cmd,
                                      std::span<const std::uint8_t> tx,
                                      std::span<std::uint8_t> rx) {
    auto selection = select(device);
    if (!selection) {
        return std::unexpected(selection.error());
    }

    /* Жодного goto out і жодного «не забути зняти CS»: деструктор Selection
       підніме дозвіл на будь-якому виході — і на ранньому return з помилкою,
       і на винятку, який кине драйвер SPI під час обміну по DMA. */
    if (!cmd.empty()) {
        if (auto r = spi.transfer(cmd, {}); !r) {
            return std::unexpected(r.error());
        }
    }
    if (!tx.empty() || !rx.empty()) {
        if (auto r = spi.transfer(tx, rx); !r) {
            return std::unexpected(r.error());
        }
    }
    return {};
}

Hc138ChipSelect::Selection::Selection(Selection&& other) noexcept
    : owner_(other.owner_), device_(other.device_) {
    other.owner_ = nullptr;
}

Hc138ChipSelect::Selection::~Selection() {
    if (owner_ != nullptr) {
        /* Ведений мусить побачити зростання CS навіть після зірваної
           транзакції — інакше він лишиться посеред недочитаної команди. */
        owner_->release();
    }
}

}  // namespace board
