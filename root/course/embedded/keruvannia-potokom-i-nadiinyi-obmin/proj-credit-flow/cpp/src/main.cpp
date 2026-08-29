// Прогін обох механізмів на віртуальному часі: на столі видно те саме, що на
// логічному аналізаторі — коли смикається /RTS і як лінк виходить зі стопора
// після втраченого кадру повернення кредитів.
#include "credit_link.hpp"
#include "flow_ring.hpp"

#include <array>
#include <cstdint>
#include <print>
#include <span>
#include <string_view>

namespace {

void demo_ring_buffer()
{
    std::uint32_t transitions = 0;

    // Лінія — звичайна лямбда: у прошивці тут був би запис у регістр GPIO.
    auto ring = flow::make_ring<256>([&transitions](bool ready) noexcept {
        ++transitions;
        std::println("    /RTS -> {:<5} (перемикань: {})", ready ? "READY" : "BUSY", transitions);
    });

    std::println("== Кільцевий буфер з гістерезисом ==");

    // Пачка від швидкого передавача: заливаємо 200 байтів без жодного читання.
    std::uint32_t pushed = 0;
    for (; pushed < 200; ++pushed) {
        if (!ring.push_from_isr(static_cast<std::uint8_t>(pushed))) {
            break;
        }
    }
    std::println("  залито {}, рівень {}, вільно {}, лінія {}", pushed, ring.level(),
                 ring.free_space(), ring.ready() ? "READY" : "BUSY");

    // Найважливіше: вичитуємо по одному байту від рівня 200 до 64. З одним
    // порогом кожен байт давав би пару перемикань лінії.
    while (ring.level() > decltype(ring)::kLowWatermark) {
        [[maybe_unused]] auto byte = ring.pop();
    }
    std::println("  рівень {}, лінія {}, усього перемикань {}", ring.level(),
                 ring.ready() ? "READY" : "BUSY", transitions);

    // Передавач, що проігнорував Busy: запас у 64 байти поглинає байти в польоті,
    // далі починається справжня втрата.
    for (std::uint32_t i = 0; i < 300; ++i) {
        [[maybe_unused]] auto ok = ring.push_from_isr(static_cast<std::uint8_t>(i));
    }
    std::println("  після переливу: рівень {}, втрачено байтів {}", ring.level(),
                 ring.overruns());

    // Вигрібання пачкою — так це робить фонове завдання, а не побайтовий цикл.
    std::array<std::uint8_t, 32> chunk{};
    while (ring.pop(chunk) > 0) {
    }
    std::println("  спорожнено: рівень {}, лінія {}\n", ring.level(),
                 ring.ready() ? "READY" : "BUSY");
}

std::span<const std::uint8_t> as_bytes(std::string_view text) noexcept
{
    return {reinterpret_cast<const std::uint8_t*>(text.data()), text.size()};
}

void demo_credit_link()
{
    using credit::Millis;

    static constexpr std::array<std::string_view, 8> messages{
        "temp=21.4", "temp=21.6", "temp=21.9", "temp=22.1",
        "temp=22.0", "temp=21.8", "temp=21.5", "temp=21.3"};

    credit::Sender tx{Millis{0}};
    credit::Receiver rx;

    // Модель шини: один кадр GRANT навмисно губимо, щоб побачити роботу таймера.
    unsigned grants_to_drop = 1;
    std::size_t next_msg = 0;
    Millis consume_at{90};

    std::println("== Кредитний автомат ==");

    for (Millis now{0}; now <= Millis{3000}; now += Millis{10}) {
        // 1. Передавач віддає чергове повідомлення, поки є баланс.
        if (next_msg < messages.size() && tx.can_send()) {
            if (auto frame = tx.encode(as_bytes(messages[next_msg]), now)) {
                const auto stored = rx.accept(*frame);
                std::println("[{:4} мс] TX->RX: DATA seq={} \"{}\", лишилось кредитів {}{}",
                             now.count(), frame->seq(), messages[next_msg], tx.credits(),
                             stored ? "" : " [ВІДКИНУТО ПРИЙМАЧЕМ]");
                ++next_msg;
            }
        }

        // 2. Таймер неактивності передавача.
        if (auto poll = tx.tick(now)) {
            std::println("[{:4} мс] TX->RX: POLL (спроба {}, зараховано cum={})", now.count(),
                         tx.polls_sent(), poll->cumulative_release());
            [[maybe_unused]] auto disposition = rx.accept(*poll);
        }

        // 3. Завдання приймача вичитує пакет із пам'яті — повільніше за передавача.
        if (now >= consume_at) {
            if (auto done = rx.take()) {
                std::println(
                    "[{:4} мс] RX    : оброблено seq={}, зайнято слотів {}, звільнено всього {}",
                    now.count(), done->seq(), rx.occupied(), rx.cumulative_release());
                consume_at = now + Millis{90};
            }
        }

        // 4. Повернення кредитів: пачкою або у відповідь на POLL.
        if (auto grant = rx.build_grant()) {
            std::println("[{:4} мс] RX->TX: GRANT cum={}", now.count(),
                         grant->cumulative_release());
            if (grants_to_drop > 0) {
                --grants_to_drop;
                std::println("[{:4} мс] ШИНА  : GRANT(cum={}) ЗАГУБЛЕНО", now.count(),
                             grant->cumulative_release());
            } else {
                tx.on_frame(*grant, now);
                std::println("[{:4} мс] TX    : зараховано cum={}, кредитів {}, стан {}",
                             now.count(), grant->cumulative_release(), tx.credits(),
                             credit::to_string(tx.state()));
            }
        }

        if (next_msg == messages.size() && rx.occupied() == 0) {
            break;
        }
        if (tx.state() == credit::LinkState::Dead) {
            std::println("        лінк визнано мертвим: далі потрібне повторне встановлення "
                         "зв'язку");
            break;
        }
    }

    const auto& tx_stats = tx.stats();
    const auto& rx_stats = rx.stats();
    std::println("\n  підсумок: надіслано {} кадрів, повернено {} кредитів, "
                 "порожніх кадрів {}, підозрілих {}",
                 tx_stats.frames_sent, tx_stats.credits_granted, tx_stats.stale_grants,
                 tx_stats.suspect_grants);
    std::println("  приймач: понад квоту {}, пропусків у нумерації {}, биті кадри {}",
                 rx_stats.over_quota, rx_stats.seq_gaps, rx_stats.malformed);
}

} // namespace

int main()
{
    demo_ring_buffer();
    demo_credit_link();
    return 0;
}
