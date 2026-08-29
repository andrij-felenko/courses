// Демонстрація: 24 команди на виконавчий вузол крізь канал, який б'є, губить,
// дублює, переставляє й ріже дані. Застосунок мусить побачити рівно 24 команди
// по одному разу й у правильному порядку.
#include <algorithm>
#include <array>
#include <chrono>
#include <format>
#include <iostream>
#include <string_view>

#include "channel.hpp"
#include "receiver.hpp"
#include "sender.hpp"

namespace {

constexpr unsigned kCommands = 24;
constexpr auto     kTimeLimit = std::chrono::milliseconds{20000};

// Виконавчий вузол: кожна команда — крок двигуна. Повторне виконання = аварія.
class Actuator {
public:
    void execute(std::uint8_t seq, link::Bytes payload) {
        if (payload.empty()) {
            return;
        }
        const unsigned index = payload[0];
        if (index != expected_index_) {
            order_broken_ = true;
            std::cout << std::format("  АВАРІЯ: застосунок побачив команду #{:02}, а чекав #{:02}\n",
                                     index, expected_index_);
        } else {
            ++expected_index_;
        }

        ++delivered_;
        const std::string_view text{reinterpret_cast<const char*>(payload.data() + 1),
                                    payload.size() - 1};
        std::cout << std::format("  виконано seq={:3}  #{:02} {}\n", seq, index, text);
    }

    [[nodiscard]] bool healthy() const noexcept {
        return !order_broken_ && delivered_ == kCommands && expected_index_ == kCommands;
    }

private:
    unsigned delivered_{0};
    unsigned expected_index_{0};
    bool     order_broken_{false};
};

void print_channel(std::string_view name, const Channel& channel) {
    const auto& s = channel.stats();
    std::cout << std::format(
        "{}: віддано {}, згинуло {}, побито {}, здубльовано {}, переставлено {}, черга переповнена {}\n",
        name, s.offered, s.dropped, s.corrupted, s.duplicated, s.reordered, s.overflow);
}

}  // namespace

int main() {
    // Шафа автоматики поруч із частотним інвертором: канал поганий в обидва боки.
    Channel forward{Channel::Profile{.drop_permille = 150, .duplicate_permille = 80,
                                     .reorder_permille = 120, .burst_permille = 120},
                    0x1234ABCDu};
    Channel backward{Channel::Profile{.drop_permille = 150, .duplicate_permille = 0,
                                      .reorder_permille = 0, .burst_permille = 80},
                     0x0BADC0DEu};

    Actuator actuator;
    link::Receiver receiver{
        [&actuator](std::uint8_t seq, link::Bytes payload) { actuator.execute(seq, payload); },
        [&backward](link::Bytes bytes) { backward.send(bytes); }};

    link::Sender sender{[&forward](link::Bytes bytes) { forward.send(bytes); }};

    unsigned next_command = 0;
    auto     now = std::chrono::milliseconds{0};
    bool     link_down = false;

    while (now < kTimeLimit) {
        // Наповнюємо вікно, доки є вільні слоти.
        while (next_command < kCommands) {
            std::array<std::uint8_t, 16> command{};
            command[0] = static_cast<std::uint8_t>(next_command);
            constexpr std::string_view text{"STEP +10mm"};
            std::ranges::copy(text, reinterpret_cast<char*>(command.data() + 1));

            const auto sent = sender.submit(link::Bytes{command.data(), 1 + text.size()}, now);
            if (!sent) {
                if (sent.error() != link::Error::WindowFull) {
                    std::cout << std::format("подача команди не вдалася: {}\n",
                                             link::describe(sent.error()));
                }
                break;
            }
            ++next_command;
        }

        if (const auto ticked = sender.tick(now); !ticked) {
            std::cout << "ліміт повторів вичерпано — вважаємо лінію розірваною\n";
            link_down = true;
            break;
        }

        forward.pump([&receiver](link::Bytes bytes) { receiver.feed(bytes); });
        backward.pump([&sender](link::Bytes bytes) { sender.feed_acks(bytes); });

        if (next_command == kCommands && sender.idle() && forward.idle() && backward.idle()) {
            break;
        }
        now += std::chrono::milliseconds{1};
    }

    std::cout << std::format("\n--- що зробив канал (за {} мс віртуального часу) ---\n",
                             now.count());
    print_channel("вперед ", forward);
    print_channel("назад  ", backward);

    const auto& fs = receiver.frame_stats();
    const auto& rs = receiver.stats();
    std::cout << "\n--- що побачив приймач ---\n";
    std::cout << std::format("цілих кадрів {}, помилок COBS {}, помилок CRC {}, переповнень {}\n",
                             fs.frames, fs.cobs_errors, fs.crc_errors, fs.overflows);
    std::cout << std::format(
        "віддано застосунку {}, дублікатів відкинуто {}, буферизовано {}, поза вікном {}\n",
        rs.delivered, rs.duplicates, rs.buffered, rs.out_of_window);

    const auto& ts = sender.stats();
    std::cout << "\n--- що робив передавач ---\n";
    std::cout << std::format(
        "нових кадрів {}, повторів {}, квитанцій {} (з них зайвих {}), втрачено {}\n",
        ts.sent, ts.retrans, ts.acked, ts.stray_ack, ts.lost);

    const bool ok = !link_down && actuator.healthy();
    std::cout << std::format("\nВЕРДИКТ: {}\n",
                             ok ? "усі команди виконано рівно по разу й у правильному порядку"
                                : "конвеєр не втримав канал");
    return ok ? 0 : 1;
}
