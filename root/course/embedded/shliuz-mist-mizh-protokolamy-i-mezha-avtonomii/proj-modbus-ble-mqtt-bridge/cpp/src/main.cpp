#include <algorithm>
#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <format>
#include <iostream>
#include <mutex>
#include <random>
#include <stop_token>
#include <string>
#include <string_view>
#include <thread>

#include "ble_scanner.hpp"
#include "modbus_master.hpp"
#include "mqtt_client.hpp"
#include "store_forward.hpp"

// Шлюз між польовим сегментом (RS-485 + BLE) і хмарним брокером MQTT.
// Три задачі, жодна не чекає на іншу; єдиний зв'язок між ними — буфер
// Store-and-Forward.

namespace {

constexpr const char* kModbusDevice = "/dev/ttyUSB0";
constexpr int kModbusBaud = 19200;
constexpr std::uint8_t kSlaveId = 1;
constexpr std::uint16_t kPressureRegister = 0x0001;  // два регістри: float32 у барах
constexpr std::uint16_t kEmergencyDumpCoil = 0x0010;
constexpr float kAlarmSetBar = 10.0F;
constexpr float kAlarmClearBar = 9.5F;  // гістерезис: інакше клапан смикався б
constexpr auto kPollPeriod = std::chrono::milliseconds{1000};

constexpr int kHciIndex = 0;

constexpr const char* kBrokerHost = "broker.plant.local";
constexpr const char* kBrokerPort = "1883";
constexpr const char* kClientId = "gw-unit1";
constexpr auto kKeepAlive = std::chrono::seconds{30};

constexpr std::size_t kFreshCapacity = 64;
constexpr std::size_t kBacklogCapacity = 4096;
constexpr double kDrainRatePerSecond = 5.0;
constexpr double kDrainBurst = 10.0;
constexpr auto kBackoffMin = std::chrono::milliseconds{1000};
constexpr auto kBackoffMax = std::chrono::milliseconds{30000};

volatile std::sig_atomic_t g_stopRequested = 0;
std::atomic<std::uint32_t> g_sequence{0};
std::mutex g_logMutex;

void onSignal(int) { g_stopRequested = 1; }

// Три потоки пишуть у той самий потік виводу — без замка рядки перепліталися б.
void logLine(std::string_view text) {
    const auto now = std::chrono::system_clock::now();
    const std::lock_guard lock{g_logMutex};
    std::cout << std::format("{:%H:%M:%S} {}\n", std::chrono::floor<std::chrono::seconds>(now), text);
    std::cout.flush();
}

// Номер послідовності й мітку часу ставить шлюз, а не давач: за розривом у seq
// сервер бачить, скільки записів згоріло в переповненому буфері.
void publish(gw::StoreForward& buffer, std::string topic, std::string_view body) {
    const std::uint32_t seq = g_sequence.fetch_add(1) + 1;
    const auto stamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                           std::chrono::system_clock::now().time_since_epoch())
                           .count();
    buffer.publish(gw::TelemetryMessage{
        .topic = std::move(topic),
        .payload = std::format(R"({{"seq":{},"ts":{},{}}})", seq, stamp, body),
        .seq = seq,
    });
}

void pollerTask(std::stop_token stop, gw::ModbusMaster& bus, gw::StoreForward& buffer) {
    bool alarmLatched = false;
    unsigned errorsInRow = 0;

    while (!stop.stop_requested()) {
        const auto cycleStart = std::chrono::steady_clock::now();
        try {
            const auto regs = bus.readHolding(kSlaveId, kPressureRegister, 2);
            if (errorsInRow >= 3) {
                publish(buffer, "plant/unit1/status/fieldbus",
                        std::format(R"("link":"up","slave":{})", kSlaveId));
            }
            errorsInRow = 0;

            const float bar = gw::ModbusMaster::regsToFloat(
                std::span<const std::uint16_t, 2>{regs.data(), 2});

            // Межа автономії проходить саме тут. Дорога до хмари й назад коштує
            // секунд і може не відбутися взагалі, а клапан треба відкрити зараз.
            if (!alarmLatched && bar > kAlarmSetBar) {
                try {
                    bus.writeCoil(kSlaveId, kEmergencyDumpCoil, true);
                    alarmLatched = true;
                    logLine(std::format("[автономія] тиск {:.2f} бар > {:.1f} — котушку 0x{:04X} увімкнено",
                                        bar, kAlarmSetBar, kEmergencyDumpCoil));
                    publish(buffer, "plant/unit1/event/alarm",
                            std::format(R"("rule":"pressure_high","p_bar":{:.2f},"action":"dump_on")", bar));
                } catch (const gw::ModbusError& error) {
                    // Засувка не спрацювала — засувка й лишається метою: латч не
                    // ставимо, наступний такт спробує знову.
                    logLine(std::format("[автономія] СКИДАННЯ НЕ ПРОЙШЛО ({}) — повтор наступним тактом",
                                        error.what()));
                    publish(buffer, "plant/unit1/event/alarm",
                            std::format(R"("rule":"pressure_high","p_bar":{:.2f},"action":"dump_failed")", bar));
                }
            } else if (alarmLatched && bar < kAlarmClearBar) {
                bus.writeCoil(kSlaveId, kEmergencyDumpCoil, false);
                alarmLatched = false;
                logLine(std::format("[автономія] тиск {:.2f} бар — аварію знято, котушку вимкнено", bar));
                publish(buffer, "plant/unit1/event/alarm",
                        std::format(R"("rule":"pressure_high","p_bar":{:.2f},"action":"dump_off")", bar));
            }

            publish(buffer, "plant/unit1/telemetry/pressure",
                    std::format(R"("dev":"boiler_1","p_bar":{:.2f},"alarm":{})", bar, alarmLatched));
        } catch (const gw::ModbusError& error) {
            ++errorsInRow;
            logLine(std::format("[modbus] вузол {}: {} (підряд {})", kSlaveId, error.what(), errorsInRow));
            // Про смерть шини сервер має дізнатися окремим повідомленням:
            // мовчання телеметрії він списав би на обрив WAN.
            if (errorsInRow == 3) {
                publish(buffer, "plant/unit1/status/fieldbus",
                        std::format(R"("link":"down","slave":{},"why":"{}")", kSlaveId, error.what()));
            }
        } catch (const std::system_error& error) {
            ++errorsInRow;
            logLine(std::format("[modbus] порт відвалився: {}", error.what()));
        }

        std::this_thread::sleep_until(cycleStart + kPollPeriod);
    }
}

void bleTask(std::stop_token stop, gw::StoreForward& buffer) {
    try {
        gw::BleScanner scanner{kHciIndex};
        logLine(std::format("[ble] пасивне сканування hci{} увімкнено", kHciIndex));

        while (!stop.stop_requested()) {
            const auto sample = scanner.next(std::chrono::milliseconds{500});
            if (!sample) {
                continue;
            }
            publish(buffer, "plant/unit1/telemetry/temperature",
                    std::format(R"("dev":"{}","t_c":{:.2f},"batt":{},"rssi":{})",
                                sample->addressText(), sample->temperatureC,
                                sample->batteryPercent, sample->rssiDbm));
        }
    } catch (const std::exception& error) {
        // Радіо не піднялося або відвалилося — це привід працювати без нього, а
        // не падати: дротова шина й аварійне правило від BLE не залежать.
        logLine(std::format("[ble] сканування зупинено ({}) — шлюз працює лише по шині", error.what()));
    }
}

void uplinkTask(std::stop_token stop, gw::StoreForward& buffer) {
    auto backoff = kBackoffMin;
    std::mt19937 rng{std::random_device{}()};

    while (!stop.stop_requested()) {
        try {
            gw::MqttClient client{kBrokerHost, kBrokerPort, kClientId, kKeepAlive};
            backoff = kBackoffMin;
            logLine("[wan] з'єднання з брокером піднято");

            double tokens = kDrainBurst;
            auto lastFill = std::chrono::steady_clock::now();

            while (!stop.stop_requested()) {
                client.serviceKeepAlive();

                const auto now = std::chrono::steady_clock::now();
                const auto elapsed = std::chrono::duration<double>{now - lastFill}.count();
                tokens = std::min(kDrainBurst, tokens + elapsed * kDrainRatePerSecond);
                lastFill = now;

                const auto lease = buffer.peek(std::chrono::milliseconds{200});
                if (!lease) {
                    continue;
                }

                // Свіже йде без обмежень, архів — лише за наявності токена:
                // інакше викачування триденної історії з'їло б увесь канал, і
                // щойно зняті показники чекали б за спиною в старих записів.
                if (lease->fromBacklog && tokens < 1.0) {
                    std::this_thread::sleep_for(std::chrono::milliseconds{50});
                    continue;
                }

                client.publishQos1(lease->msg.topic, lease->msg.payload);
                buffer.commit(*lease);
                if (lease->fromBacklog) {
                    tokens -= 1.0;
                }
            }
        } catch (const std::exception& error) {
            // Неспідтверджене повідомлення лишається в черзі й піде після
            // перепідключення; брокер може отримати дублікат — нормальна ціна
            // доставки «щонайменше раз».
            const auto stats = buffer.stats();
            // Джитер обов'язковий: після падіння базової станції сотні шлюзів
            // прокидаються разом, і рівний відступ звів би їх в один залп.
            std::uniform_int_distribution<int> jitter{static_cast<int>(backoff.count()) / 2,
                                                      static_cast<int>(backoff.count()) * 3 / 2};
            const std::chrono::milliseconds wait{jitter(rng)};
            logLine(std::format("[wan] {}; повтор через {} мс; у буфері {}+{}, втрачено {}",
                                error.what(), wait.count(), stats.fresh, stats.backlog, stats.dropped));
            std::this_thread::sleep_for(wait);
            backoff = std::min(kBackoffMax, backoff * 2);
        }
    }
}

}  // namespace

int main() {
    std::signal(SIGINT, onSignal);
    std::signal(SIGTERM, onSignal);
    // Запис у мертвий сокет не повинен убивати шлюз — помилку поверне write().
    std::signal(SIGPIPE, SIG_IGN);

    gw::StoreForward buffer{kFreshCapacity, kBacklogCapacity};

    try {
        gw::ModbusMaster bus{kModbusDevice, kModbusBaud, std::chrono::milliseconds{500}};
        logLine(std::format("=== шлюз піднято: {} @ {}, брокер {}:{} ===", kModbusDevice,
                            kModbusBaud, kBrokerHost, kBrokerPort));

        // Кожен jthread у деструкторі сам просить зупинки й дочікується потоку,
        // тож вихід зі області видимості — це і є впорядкована зупинка.
        std::jthread poller{[&](std::stop_token stop) { pollerTask(std::move(stop), bus, buffer); }};
        std::jthread ble{[&](std::stop_token stop) { bleTask(std::move(stop), buffer); }};
        std::jthread uplink{[&](std::stop_token stop) { uplinkTask(std::move(stop), buffer); }};

        while (g_stopRequested == 0) {
            std::this_thread::sleep_for(std::chrono::seconds{5});
            const auto stats = buffer.stats();
            logLine(std::format("[буфер] свіжих {}, архівних {}, втрачено назавжди {}", stats.fresh,
                                stats.backlog, stats.dropped));
        }

        logLine("зупинка за сигналом…");
    } catch (const std::exception& error) {
        std::cerr << std::format("шлюз не піднявся: {}\n", error.what());
        return 1;
    }

    logLine("=== шлюз зупинено ===");
    return 0;
}
