// main.cpp — симулятор польового вузла: телеметрія за розкладом,
// команди зі шлюзу — щойно прийдуть, квитанція на кожну свою команду.
//
// Запуск:  ./node [node_id] [host] [port]     типово: 42 127.0.0.1 9000
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <format>
#include <iostream>
#include <string>
#include <thread>
#include <type_traits>
#include <variant>

#include "link.hpp"
#include "node.hpp"
#include "protocol.hpp"

namespace {

using namespace std::chrono_literals;

constexpr auto kTelemetryPeriod = 2000ms;
constexpr auto kPollSlice = 200ms;
constexpr auto kReconnectDelay = 1000ms;

volatile std::sig_atomic_t g_stop = 0;

void on_sigint(int) { g_stop = 1; }

std::string format_temp(std::int16_t c100) {
    return std::format("{}.{:02} °C", c100 / 100, std::abs(c100 % 100));
}

// Розібраний кадр приходить як variant — розкладаємо його візитором,
// а не switch за байтом типу: новий тип кадру перестане компілюватися мовчки.
void handle(field::EdgeNode& node, field::TcpLink& link, const field::Frame& frame) {
    std::visit(
        [&](const auto& f) {
            using T = std::decay_t<decltype(f)>;
            if constexpr (std::is_same_v<T, field::Command>) {
                auto ack = node.apply(f);
                if (!ack) {
                    return;   // кадр для сусіднього вузла
                }
                std::cout << std::format("[node {}] команда seq={} код 0x{:02X} → {}\n",
                                         node.id(), f.seq, static_cast<int>(f.id),
                                         ack->status == field::AckStatus::Ok
                                             ? (node.relay_on() ? "реле увімкнено" : "реле вимкнено")
                                             : "відхилено");
                if (auto sent = link.send(field::encode(*ack)); !sent) {
                    std::cerr << std::format("[node {}] квитанцію не віддано — {}\n", node.id(),
                                             field::describe(sent.error()));
                }
            } else {
                // Телеметрію й чужі квитанції вузол не обробляє: у каналі
                // вони можливі, але його справи не стосуються.
            }
        },
        frame);
}

// Одна сесія зв'язку: живе, поки канал цілий.
void run_session(field::EdgeNode& node, field::TcpLink& link) {
    auto next_tx = std::chrono::steady_clock::now();

    while (g_stop == 0) {
        auto got = link.read_frame(kPollSlice);
        if (!got) {
            std::cerr << std::format("[node {}] канал урвався — {}\n", node.id(),
                                     field::describe(got.error()));
            return;
        }
        if (got->has_value()) {
            if (auto decoded = field::decode(**got)) {
                handle(node, link, *decoded);
            } else {
                std::cerr << std::format("[node {}] кадр відкинуто — {}\n", node.id(),
                                         field::describe(decoded.error()));
            }
        }

        if (std::chrono::steady_clock::now() >= next_tx) {
            const auto telemetry = node.sample();
            if (auto sent = link.send(field::encode(telemetry)); !sent) {
                std::cerr << std::format("[node {}] телеметрію не віддано — {}\n", node.id(),
                                         field::describe(sent.error()));
                return;
            }
            std::cout << std::format("[node {}] seq={}  {}  {} мВ  реле={}\n", node.id(),
                                     telemetry.seq, format_temp(telemetry.temp_c100),
                                     telemetry.battery_mv,
                                     telemetry.flags.relay_on ? "увімкнено" : "вимкнено");
            next_tx += kTelemetryPeriod;
        }
    }
}

}  // namespace

int main(int argc, char** argv) {
    const auto node_id = static_cast<std::uint16_t>(argc > 1 ? std::stoul(argv[1]) : 42);
    const std::string host = argc > 2 ? argv[2] : "127.0.0.1";
    const std::string port = argc > 3 ? argv[3] : "9000";

    std::signal(SIGINT, on_sigint);

    field::EdgeNode node{node_id};
    std::cout << std::format("[node {}] старт, шлюз {}:{}\n", node_id, host, port);

    while (g_stop == 0) {
        auto link = field::TcpLink::connect(host, port);
        if (!link) {
            // Шлюз піднімається довше за вузол — це не привід здаватися.
            std::cerr << std::format("[node {}] {}\n", node_id, link.error());
            std::this_thread::sleep_for(kReconnectDelay);
            continue;
        }

        std::cout << std::format("[node {}] канал відкрито\n", node_id);
        run_session(node, *link);
        std::cout << std::format("[node {}] сесію закрито, викинуто на ресинхронізації {} байтів\n",
                                 node_id, link->resync_drops());

        if (g_stop == 0) {
            std::this_thread::sleep_for(kReconnectDelay);
        }
    }

    std::cout << std::format("\n[node {}] зупинка за SIGINT\n", node_id);
    return 0;
}
