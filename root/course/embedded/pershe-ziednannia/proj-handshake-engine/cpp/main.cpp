#include "handshake_engine.h"
#include "udp_link.h"

#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <csignal>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

namespace {

std::atomic<bool> g_stop{false};

extern "C" void onSignal(int) {
    g_stop.store(true);
}

// Потокобезпечна межа між комунікаційним потоком і потоком інтерфейсу.
// Малює лише той, хто забирає події; парсер про малювання не знає нічого.
class EventQueue {
public:
    void push(EngineEvent event) {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            m_items.push_back(std::move(event));
        }
        m_cv.notify_one();
    }

    std::vector<EngineEvent> drain(std::chrono::milliseconds wait) {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_cv.wait_for(lock, wait, [this] { return !m_items.empty(); });
        std::vector<EngineEvent> out;
        out.swap(m_items);
        return out;
    }

private:
    std::mutex m_mutex;
    std::condition_variable m_cv;
    std::vector<EngineEvent> m_items;
};

// Автомат, посаджений на UDP. Уся прив'язка до транспорту — три рядки.
class UdpEngine final : public GcsHandshakeEngine {
public:
    explicit UdpEngine(UdpLink& link) : m_link(link) {}

protected:
    void sendPacket(std::span<const std::uint8_t> frame) override {
        m_link.send(frame);
    }

private:
    UdpLink& m_link;
};

struct Endpoint {
    std::string host;
    std::uint16_t port;
};

Endpoint parseEndpoint(std::string_view text) {
    const auto colon = text.rfind(':');
    if (colon == std::string_view::npos || colon + 1 >= text.size()) {
        throw std::invalid_argument("очікую host:port, отримав: " + std::string(text));
    }
    const int port = std::stoi(std::string(text.substr(colon + 1)));
    if (port <= 0 || port > 65535) {
        throw std::invalid_argument("порт поза межами: " + std::string(text.substr(colon + 1)));
    }
    return Endpoint{std::string(text.substr(0, colon)), static_cast<std::uint16_t>(port)};
}

// Комунікаційний потік: байти → mavlink_parse_char → кадри → автомат.
void ioLoop(UdpLink& link, GcsHandshakeEngine& engine, EventQueue& queue) {
    std::array<std::uint8_t, 2048> buffer{};
    mavlink_message_t msg{};
    mavlink_status_t status{};
    unsigned drops = 0;

    auto note = [&](std::string text) {
        EngineEvent ev;
        ev.kind = EngineEvent::Kind::Log;
        ev.state = engine.state();
        ev.text = std::move(text);
        queue.push(std::move(ev));
    };

    try {
        while (!g_stop.load()) {
            const std::size_t n = link.receive(buffer, 10);
            if (link.takePeerUpdate()) {
                note("кадри йдуть від " + link.peerName());
            }

            for (std::size_t i = 0; i < n; ++i) {
                if (mavlink_parse_char(MAVLINK_COMM_0, buffer[i], &msg, &status) == MAVLINK_FRAMING_OK) {
                    engine.onMavlinkMessage(msg);
                }
            }

            if (status.packet_rx_drop_count != drops) {
                drops = status.packet_rx_drop_count;
                note("парсер відкинув побитих кадрів усього: " + std::to_string(drops));
            }

            engine.tick();
        }
    } catch (const std::exception& e) {
        note(std::string("канал зламався: ") + e.what());
        g_stop.store(true);
    }
}

void printParam(const std::unordered_map<std::string, float>& params, const char* name) {
    const auto it = params.find(name);
    if (it != params.end()) {
        std::cout << "      " << name << " = " << it->second << "\n";
    }
}

} // namespace

int main(int argc, char** argv) {
    const std::string address = (argc > 1) ? argv[1] : "0.0.0.0:14550";

    std::signal(SIGINT, onSignal);
    std::signal(SIGTERM, onSignal);

    try {
        const Endpoint endpoint = parseEndpoint(address);
        UdpLink link(endpoint.host, endpoint.port);
        std::cout << "[GCS] слухаю " << endpoint.host << ":" << endpoint.port << "\n";

        EventQueue queue;
        UdpEngine engine(link);
        engine.setEventSink([&queue](EngineEvent ev) { queue.push(std::move(ev)); });
        engine.start();

        std::thread io([&] { ioLoop(link, engine, queue); });

        int exit_code = 0;
        std::cout << std::fixed << std::setprecision(7);

        // «Потік інтерфейсу»: тільки готові структури, жодного розбору байтів.
        while (!g_stop.load()) {
            for (auto& ev : queue.drain(std::chrono::milliseconds(100))) {
                switch (ev.kind) {
                    case EngineEvent::Kind::Log:
                        std::cout << "[" << stateName(ev.state) << "] " << ev.text << "\n";
                        break;

                    case EngineEvent::Kind::StateChanged:
                        std::cout << ">>> стан: " << ev.text << "\n";
                        if (ev.state == HandshakeState::Operational) {
                            std::cout << ">>> СТАНЦІЯ ГОТОВА: зв'язок узгоджено повністю\n";
                        }
                        if (ev.state == HandshakeState::Failed) {
                            exit_code = 1;
                            g_stop.store(true);
                        }
                        break;

                    case EngineEvent::Kind::VehicleFound:
                        std::cout << "    апарат SysID=" << static_cast<int>(ev.vehicle.sysid)
                                  << " CompID=" << static_cast<int>(ev.vehicle.compid)
                                  << " type=" << static_cast<int>(ev.vehicle.type)
                                  << " autopilot=" << static_cast<int>(ev.vehicle.autopilot)
                                  << " armed=" << (ev.vehicle.armed ? "так" : "ні") << "\n";
                        break;

                    case EngineEvent::Kind::ParamsReady:
                        std::cout << "    таблиця параметрів: " << ev.params.size() << " записів\n";
                        printParam(ev.params, "SYSID_THISMAV");
                        printParam(ev.params, "FRAME_CLASS");
                        printParam(ev.params, "BATT_CAPACITY");
                        printParam(ev.params, "WPNAV_SPEED");
                        break;

                    case EngineEvent::Kind::MissionReady:
                        std::cout << "    польотний план: " << ev.mission.size() << " точок\n";
                        for (const auto& wp : ev.mission) {
                            std::cout << "      #" << wp.seq << " cmd=" << wp.command
                                      << " lat=" << wp.lat_e7 / 1e7
                                      << " lon=" << wp.lon_e7 / 1e7
                                      << " alt=" << wp.alt_m << " м\n";
                        }
                        break;
                }
            }
        }

        io.join();
        return exit_code;
    } catch (const std::exception& e) {
        std::cerr << "[GCS] фатально: " << e.what() << "\n";
        return 1;
    }
}
