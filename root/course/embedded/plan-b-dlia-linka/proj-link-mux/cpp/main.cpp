// Прогін диспетчера на моделі польоту: 20 секунд із заглушенням основного
// каналу, провалом резерву й поверненням. Час іде кроком 10 мс — у прошивці
// на цьому місці таймерне переривання й HAL_GetTick().
#include "arbiter.hpp"
#include "spsc_ring.hpp"

#include <array>
#include <cstdint>
#include <format>
#include <iostream>

using namespace linkmux;

namespace {

constexpr Millis kTick{10};
constexpr Millis kSimEnd{20000};
constexpr Millis kJamStart{3000};      // завада по основному каналу
constexpr Millis kJamEnd{11000};
constexpr Millis kFallJamStart{5500};  // заглушили ще й резерв
constexpr Millis kFallJamEnd{9500};

Millis gNow{0};

// --- Модель ефіру: кадр летить не миттєво, і саме тому кадри міняються
// місцями. Наземна станція розбирає їх ковзним вікном дедуплікації.
struct AirFrame {
    bool          busy{false};
    std::uint16_t seq{0};
    Millis        arrive{0};
};

std::array<AirFrame, 64> gAir{};
DedupWindow              gGround{};
std::uint32_t            gGroundOk{0};
std::uint32_t            gAirLost{0};

void airLaunch(std::uint16_t seq, Millis arrive) noexcept {
    for (auto& slot : gAir) {
        if (!slot.busy) {
            slot = AirFrame{true, seq, arrive};
            return;
        }
    }
    ++gAirLost;
}

void groundPoll(Millis now) noexcept {
    for (auto& slot : gAir) {
        if (!slot.busy || now < slot.arrive) {
            continue;
        }
        slot.busy = false;
        if (gGround.accept(slot.seq)) {
            ++gGroundOk;
        }
    }
}

// --- Драйвер трансивера: тут закінчується арбітр і починається залізо ---
class SimRadio final : public Transceiver {
public:
    SimRadio(std::string_view name, Millis airTime, Millis slot) noexcept
        : name_(name), airTime_(airTime), slot_(slot) {}

    [[nodiscard]] std::expected<std::size_t, TxError> send(const Frame& frame) noexcept override {
        if (faulty_) {
            return std::unexpected(TxError::HardwareFault);   // SPI не відповів
        }
        airLaunch(frame.seq, gNow + airTime_);
        return frame.len;
    }

    void setMode(RadioMode mode) noexcept override {
        std::cout << std::format("        {:<10} -> {}\n", name_, modeName(mode));
    }

    [[nodiscard]] std::string_view name() const noexcept override { return name_; }
    [[nodiscard]] Millis airTime() const noexcept override { return airTime_; }
    [[nodiscard]] Millis slot() const noexcept override { return slot_; }

private:
    std::string_view name_;
    Millis           airTime_;
    Millis           slot_;
    bool             faulty_{false};
};

// --- Модель радіообстановки ---
struct PrimaryFrame {
    bool         arrives;
    std::int16_t rssiDbm;
};

PrimaryFrame primaryFrame(Millis now) noexcept {
    if (now < kJamStart || now >= kJamEnd) {
        return {true, -62};                          // 100 Гц телеметрії з землі
    }
    if (now < kJamStart + Millis{200}) {
        // Завада наростає: крізь неї пролазить кожен третій кадр
        return {(now.count() / kTick.count()) % 3 == 0, -104};
    }
    return {false, -110};                            // повна тиша
}

bool fallbackFrame(Millis now) noexcept {
    if (now.count() % 200 != 0) {
        return false;                                // маяк резерву 5 Гц
    }
    return now < kFallJamStart || now >= kFallJamEnd;
}

// Контекст переривання: перекласти кадр у кільце й вийти. Жодної математики.
void rxIsr(SpscRing<Frame, 16>& ring, BearerId id, std::uint16_t seq,
           std::int16_t rssi, std::int8_t snr, Millis now) noexcept {
    Frame frame;
    frame.seq     = seq;
    frame.stampMs = static_cast<std::uint32_t>(now.count());
    frame.bearer  = static_cast<std::uint8_t>(id);
    frame.rssiDbm = rssi;
    frame.snrDb   = snr;
    static_cast<void>(ring.push(frame));   // переповнення пораховане всередині
}

}  // namespace

int main() {
    SimRadio wifi{"2.4G-OFDM", Millis{3}, Millis{10}};
    SimRadio lora{"868M-LoRa", Millis{90}, Millis{200}};

    MultiLinkArbiter arbiter{wifi, lora, Millis{0}};
    SpscRing<Frame, 16> rxRing{};

    const std::array<std::uint8_t, 48>  telemetry{};
    const std::array<std::uint8_t, 200> video{};
    const std::array<std::uint8_t, 12>  command{};

    std::uint16_t primSeq = 0;
    std::uint16_t fallSeq = 0;
    std::uint32_t tlmOk = 0, vidOk = 0, vidRefused = 0, critOk = 0, critLost = 0;

    ArbiterState lastState = arbiter.state();
    std::cout << std::format("  0.00 с  стан: {}\n", stateName(lastState));

    for (gNow = Millis{0}; gNow <= kSimEnd; gNow += kTick) {
        const Millis now = gNow;

        // 1. Переривання приймачів. Лічильник кадру росте завжди: кадр міг
        //    вилетіти з землі й не долетіти — саме це й дає розрив у seq.
        const auto [primArrives, primRssi] = primaryFrame(now);
        const std::uint16_t pseq = primSeq++;
        if (primArrives) {
            rxIsr(rxRing, BearerId::Primary, pseq, primRssi,
                  static_cast<std::int8_t>(primRssi < -100 ? -4 : 12), now);
        }
        if (now.count() % 200 == 0) {
            const std::uint16_t fseq = fallSeq++;
            if (fallbackFrame(now)) {
                rxIsr(rxRing, BearerId::Fallback, fseq, -95, 5, now);
            }
        }

        // 2. Задача арбітра розбирає кільце й рахує метрики
        while (const auto frame = rxRing.pop()) {
            arbiter.onFrameReceived(static_cast<BearerId>(frame->bearer), *frame, now);
        }

        // 3. Автомат станів — кожні 10 мс
        arbiter.update(now);

        // 4. Політний контролер віддає свої пакети
        if (now.count() % 20 == 0 && arbiter.routePacket(Priority::Telemetry, telemetry, now)) {
            ++tlmOk;
        }
        if (now.count() % 50 == 0) {
            if (const auto rc = arbiter.routePacket(Priority::Video, video, now); rc) {
                ++vidOk;
            } else if (rc.error() == TxError::NoBandwidth) {
                ++vidRefused;
            }
        }
        if (now.count() % 1000 == 0) {
            if (arbiter.routePacket(Priority::Critical, command, now)) {
                ++critOk;
            } else {
                ++critLost;   // верхній рівень тут вмикає автономне повернення
            }
        }

        // 5. Диспетчер віддає черги в ефір, 6. земля приймає, що долетіло
        static_cast<void>(arbiter.pump(now));
        groundPoll(now);

        if (arbiter.state() != lastState) {
            lastState = arbiter.state();
            std::cout << std::format("{:6.2f} с  стан: {:<22} носій: {:<10} PER основного {}%\n",
                                     now.count() / 1000.0, stateName(lastState),
                                     arbiter.bearerName(arbiter.activeBearer()),
                                     arbiter.quality(BearerId::Primary).per());
        }
    }

    std::cout << "\n== Підсумок 20 с ==\n";
    for (const BearerId id : {BearerId::Primary, BearerId::Fallback}) {
        std::cout << std::format("{:<10} кадрів {:5}, помилок драйвера {}, PER {}%, RSSI {} dBm\n",
                                 arbiter.bearerName(id), arbiter.txFrames(id),
                                 arbiter.txErrors(id), arbiter.quality(id).per(),
                                 arbiter.quality(id).rssiDbm());
    }
    std::cout << std::format("телеметрія: узято {}, витіснено старих {}\n",
                             tlmOk, arbiter.dropped(Priority::Telemetry));
    std::cout << std::format("відео: узято {}, відмовлено на резерві {}, скинуто чергою {}\n",
                             vidOk, vidRefused, arbiter.dropped(Priority::Video));
    std::cout << std::format("критичні: узято {}, не взято через блекаут {}\n", critOk, critLost);
    std::cout << std::format("земля: прийнято {}, дублікатів {}, спізнілих поза вікном {}\n",
                             gGroundOk, gGround.duplicates(), gGround.tooOld());
    std::cout << std::format("перемикань стану {}, переповнень RX-кільця {}, втрачено в моделі ефіру {}\n",
                             arbiter.switches(), rxRing.overruns(), gAirLost);
    return 0;
}
