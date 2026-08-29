// Прогін чотирьох сценаріїв розділу 7 профілю на симульованому радіоканалі:
// один вузол, один-два пульти, керований годинник і керовані втрати кадрів.
#include "sbo/gcs.hpp"
#include "sbo/node.hpp"

#include <format>
#include <iostream>
#include <optional>
#include <vector>

namespace {

using namespace sbo;

// Ефір: ковтає задану кількість найближчих кадрів.
class Link {
public:
    explicit Link(unsigned drops) : drops_left_{drops} {}

    std::optional<Frame> send(Node& node, Ms now, std::span<const std::uint8_t> frame) {
        if (drops_left_ > 0) {
            --drops_left_;
            std::cout << "    [ефір] кадр загублено\n";
            return std::nullopt;
        }
        auto answer = node.handle(frame, now);
        if (!answer) return std::nullopt;

        // Квитанція теж їде дротом: пульт бачить лише байти.
        const auto wire = encode(*answer);
        auto parsed = decode(wire);
        if (!parsed) {
            std::cout << "    [пульт] квитанція не пройшла перевірку CRC\n";
            return std::nullopt;
        }
        return *parsed;
    }

private:
    unsigned drops_left_;
};

void show(const Frame& r) {
    std::cout << std::format("    борт -> пульт: {:<12} стан={:<9} токен=0x{:08X} вікно={} мс",
                             name(r.type), name(r.state), r.token, r.window.count());
    if (const auto why = r.reason()) {
        std::cout << std::format(" причина={}", name(*why));
    }
    std::cout << '\n';
}

std::optional<Frame> exchange(Link& air, Node& node, Gcs& gcs, Ms now,
                              std::span<const std::uint8_t> frame) {
    auto reply = air.send(node, now, frame);
    if (reply) {
        gcs.on_reply(*reply);
        show(*reply);
    }
    return reply;
}

void scenario_a() {
    std::cout << "\n=== Сценарій А: номінальна транзакція (з утратою першого кадру) ===\n";

    Node node{0x02, 0xC0FFEEu};
    Gcs gcs{kAddrGcs};
    Link air{1};
    Ms now{0};

    bool acked = false;
    for (unsigned attempt = 0; attempt <= kRetries && !acked; ++attempt) {
        std::cout << std::format("  спроба {}: SELECT_REQ cmd=0x0101 вікно=5000 мс\n",
                                 attempt + 1);
        const auto frame = gcs.select(0x02, Comp::Esc, Cmd::EmergencyMotorCut, Ms{5000});
        const auto reply = exchange(air, node, gcs, now, frame);
        acked = reply && reply->type == MsgType::SelectAck;
        if (!acked) now += kAckWait;    // вікно T_ack_wait сплило — повтор
    }
    if (!acked) {
        std::cout << "  селекція не вдалася, оператор бачить відмову\n";
        return;
    }

    now += Ms{1500};                    // оператор тисне кнопку через 1.5 с
    node.tick(now);
    std::cout << std::format("  t={} мс: залишок вікна {} мс, OPERATE_REQ з токеном 0x{:08X}\n",
                             now.count(), node.remaining(now).count(), gcs.token());
    exchange(air, node, gcs, now, gcs.operate());

    std::cout << std::format("  живлення моторів: {}, стан селектора: {}\n",
                             node.actuators().motors_live ? "увімкнене" : "ЗНЯТО",
                             name(node.state()));
}

void scenario_b() {
    std::cout << "\n=== Сценарій Б: вікно дійсності сплило ===\n";

    Node node{0x02, 0x1BADB002u};
    Gcs gcs{kAddrGcs};
    Link air{0};
    Ms now{0};

    exchange(air, node, gcs, now, gcs.select(0x02, Comp::Fc, Cmd::ForceDisarm, Ms{5000}));
    const auto stale = gcs.token();

    now += Ms{8000};                    // оператор відволікся на вісім секунд
    node.tick(now);
    std::cout << std::format("  t={} мс: стан борту {}, прапорці 0x{:02X}\n",
                             now.count(), name(node.state()), node.heartbeat_flags());

    gcs.restore_token(stale);           // пульт іще вірить у свій токен
    exchange(air, node, gcs, now, gcs.operate());
    if (const auto why = gcs.last_error()) {
        std::cout << std::format("  пульт бачить причину {} і вимагає повторної селекції\n",
                                 name(*why));
    }
}

void scenario_c() {
    std::cout << "\n=== Сценарій В: колізія двох пультів ===\n";

    Node node{0x02, 0x5EED0002u};
    Gcs commander{kAddrGcs};
    Gcs payload_op{kAddrRelay};
    Link air{0};
    Ms now{0};

    std::cout << "  пульт командира (0xFE) бере замок\n";
    exchange(air, node, commander, now,
             commander.select(0x02, Comp::Esc, Cmd::EmergencyMotorCut, Ms{5000}));

    now += Ms{500};
    std::cout << std::format(
        "  t={} мс: пульт оператора навантаження (0xFD) пробує той самий борт\n",
        now.count());
    exchange(air, node, payload_op, now,
             payload_op.select(0x02, Comp::Fc, Cmd::PayloadDropActuate, Ms{5000}));
    if (const auto why = payload_op.last_error()) {
        std::cout << std::format("  на екрані другого пульта: «борт заблоковано» ({})\n",
                                 name(*why));
    }

    // Чужий CANCEL_REQ замка не знімає.
    exchange(air, node, payload_op, now, payload_op.cancel());
    std::cout << std::format("  замок після чужого скасування: {}\n", name(node.state()));
}

void scenario_d() {
    std::cout << "\n=== Сценарій Г: критична команда на широкомовну адресу ===\n";

    Node node{0x02, 0xDEADBEEFu};
    Gcs rogue{kAddrGcs};
    Link air{0};
    const Ms now{0};

    // Скомпрометований скрипт шле OPERATE_REQ усім одразу.
    (void)rogue.select(kAddrBroadcast, Comp::Esc, Cmd::EmergencyMotorCut, Ms{5000});
    const auto reply = air.send(node, now, rogue.operate());
    std::cout << std::format("  відповідь в ефір: {}, у журналі безпеки: {} відкидань\n",
                             reply ? "є" : "немає", node.security_drops());
    std::cout << std::format("  живлення моторів: {}\n",
                             node.actuators().motors_live ? "увімкнене" : "ЗНЯТО");

    // Широкомовна телеметрія — звичайний клас, її фільтр пропускає.
    Gcs gcs{kAddrGcs};
    (void)gcs.select(kAddrBroadcast, Comp::Fc, Cmd::RequestTelemetry, Ms{0});
    if (const auto pong = air.send(node, now, gcs.operate())) {
        show(*pong);
    }
}

void frame_dump() {
    std::cout << "\n=== Розклад байтів SELECT_REQ (розділ 8) ===\n";

    Gcs gcs{kAddrGcs};
    const auto frame = gcs.select(0x02, Comp::Fc, Cmd::EmergencyMotorCut, Ms{5000});
    for (std::uint8_t byte : frame) {
        std::cout << std::format("{:02X} ", byte);
    }
    std::cout << std::format("\n  CRC-16-CCITT тіла: 0x{:04X}\n",
                             crc16(std::span{frame}.first(frame.size() - kCrcLen)));
}

}  // namespace

int main() {
    frame_dump();
    scenario_a();
    scenario_b();
    scenario_c();
    scenario_d();
    return 0;
}
