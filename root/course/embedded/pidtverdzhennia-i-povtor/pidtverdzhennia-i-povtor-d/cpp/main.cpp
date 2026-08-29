// main.cpp — демонстрація Stop-and-Wait ARQ на віртуальному каналі.
//
// Модель: віртуальний годинник із тіком 1 мс, одностороння затримка,
// втрати й завади з детермінованим генератором (щоб прогін відтворювався).
// Вузол A шле команди, вузол B їх приймає й квитує.
#include "receiver.hpp"
#include "sender.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <print>
#include <random>
#include <span>
#include <string_view>
#include <vector>

namespace {

using Ms = std::chrono::milliseconds;

std::string_view asText(std::span<const std::uint8_t> bytes)
{
    return std::string_view{reinterpret_cast<const char*>(bytes.data()), bytes.size()};
}

class Channel {
public:
    Channel(Ms delay, unsigned dropPct, unsigned corruptPct, std::uint32_t seed)
        : delay_{delay}, dropPct_{dropPct}, corruptPct_{corruptPct}, rng_{seed} {}

    void send(bool towardReceiver, std::span<const std::uint8_t> frame, Ms now)
    {
        const std::string_view dir = towardReceiver ? "A→B" : "B→A";
        const unsigned dice = dice_(rng_);

        if (dice < dropPct_) {
            std::println("[{:5} мс] {}  кадр загублено в каналі", now.count(), dir);
            return;
        }

        Packet packet;
        packet.len = frame.size();
        std::ranges::copy(frame, packet.bytes.begin());
        packet.due             = now + delay_;
        packet.towardReceiver  = towardReceiver;

        if (dice < dropPct_ + corruptPct_) {
            // Псуємо байт даних, а в короткій квитанції — байт номера.
            const std::size_t victim =
                packet.len > arq::kCtrlFrame ? arq::kHeaderLen : std::size_t{2};
            packet.bytes[victim] ^= 0x20;
            std::println("[{:5} мс] {}  завада перевернула біт у байті {}",
                         now.count(), dir, victim);
        }
        inFlight_.push_back(packet);
    }

    // dispatch(towardReceiver, wire) — обробник кадру сам кладе в канал
    // відповідь, тому спершу забираємо готові пакети, а вже потім віддаємо.
    template <typename Dispatch>
    void pump(Ms now, Dispatch&& dispatch)
    {
        std::vector<Packet> ready;
        const auto tail = std::ranges::partition(
            inFlight_, [now](const Packet& p) { return p.due > now; });
        ready.assign(tail.begin(), tail.end());
        inFlight_.erase(tail.begin(), tail.end());

        for (const Packet& p : ready) {
            dispatch(p.towardReceiver, std::span<const std::uint8_t>{p.bytes.data(), p.len});
        }
    }

private:
    struct Packet {
        std::array<std::uint8_t, arq::kMaxFrame> bytes{};
        std::size_t len{0};
        Ms          due{0};
        bool        towardReceiver{true};
    };

    std::vector<Packet> inFlight_;
    Ms                  delay_;
    unsigned            dropPct_;
    unsigned            corruptPct_;
    std::mt19937        rng_;
    std::uniform_int_distribution<unsigned> dice_{0, 99};
};

constexpr std::array<std::string_view, 5> kCommands{
    "ARM MOTORS", "SET SPEED 120", "GET STATUS", "STOP", "DISARM"};

std::span<const std::uint8_t> bytesOf(std::string_view text)
{
    return std::span<const std::uint8_t>{reinterpret_cast<const std::uint8_t*>(text.data()),
                                         text.size()};
}

} // namespace

int main()
{
    constexpr Ms kDelay{8};
    constexpr unsigned kDropPct = 20;
    constexpr unsigned kCorruptPct = 15;

    Ms now{0};
    Channel channel{kDelay, kDropPct, kCorruptPct, 0x20260829u};

    arq::Receiver receiver{
        [&](std::span<const std::uint8_t> wire) { channel.send(false, wire, now); },
        [&](std::span<const std::uint8_t> payload) {
            std::println("[{:5} мс] B: додатку віддано «{}»", now.count(), asText(payload));
        }};

    std::size_t nextCommand = 0;
    bool inFlight = false;
    bool linkLost = false;
    const arq::RtoEstimator* rto = nullptr; // заповнюємо одразу після конструювання

    arq::Sender sender{
        [&](std::span<const std::uint8_t> wire) { channel.send(true, wire, now); },
        [&](bool delivered, std::uint8_t seq) {
            if (delivered) {
                std::println("[{:5} мс] A: seq={} підтверджено (SRTT={} мс, RTO={} мс)",
                             now.count(), seq,
                             rto->smoothedRtt().count(), rto->value().count());
            } else {
                std::println("[{:5} мс] A: seq={} не доставлено за {} спроб — зв'язок втрачено",
                             now.count(), seq, arq::kMaxRetries);
                linkLost = true;
            }
            inFlight = false;
        }};
    rto = &sender.rto();

    std::println("Stop-and-Wait ARQ: втрати {}%, спотворення {}%, затримка {} мс в один бік\n",
                 kDropPct, kCorruptPct, kDelay.count());

    for (; now < Ms{20000}; now += Ms{1}) {
        channel.pump(now, [&](bool towardReceiver, std::span<const std::uint8_t> wire) {
            if (towardReceiver) {
                receiver.onWire(wire);
            } else {
                sender.onWire(wire, now);
            }
        });
        sender.poll(now);

        if (linkLost) {
            break;
        }
        if (!inFlight) {
            if (nextCommand >= kCommands.size()) {
                break; // усі команди підтверджено
            }
            if (sender.state() == arq::SenderState::Idle) {
                const std::string_view command = kCommands[nextCommand];
                std::println("[{:5} мс] A: команда «{}» → кадр seq={}",
                             now.count(), command, sender.seq());
                if (sender.send(bytesOf(command), now)) {
                    ++nextCommand;
                    inFlight = true;
                } else {
                    std::println("[{:5} мс] A: кадр не сформовано, команду пропущено",
                                 now.count());
                    ++nextCommand;
                }
            }
        }
    }

    const auto& tx = sender.stats();
    const auto& rx = receiver.stats();
    std::println("\n--- Підсумок ({} мс модельного часу) ---", now.count());
    std::println("A: нових кадрів {}, повторів {}, підтверджено {}, відмов {}, сміття {}",
                 tx.sent, tx.retransmitted, tx.acked, tx.failed, tx.stray);
    std::print("B: доставлено {}, дублікатів відсіяно {}, побитих кадрів {}",
               rx.delivered, rx.duplicates, rx.corrupted);
    if (const auto err = receiver.lastError(); err) {
        std::print(" (остання причина: {})", arq::describe(*err));
    }
    std::println("\nПідсумковий RTO {} мс при SRTT {} мс",
                 sender.rto().value().count(), sender.rto().smoothedRtt().count());
    return 0;
}
