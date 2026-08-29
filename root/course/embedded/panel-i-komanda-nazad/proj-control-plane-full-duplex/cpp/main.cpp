/* Прошивка вузла: мережевий потік, потік воркера і стенд замість заліза.
   Збірка: c++ -std=c++23 -Wall -Wextra -pthread *.cpp -o fw */

#include "actuator.hpp"
#include "dedup_ring.hpp"
#include "protocol.hpp"
#include "valve.hpp"

#include <chrono>
#include <format>
#include <iostream>
#include <string>
#include <string_view>
#include <thread>

using namespace std::chrono_literals;

namespace {

std::chrono::seconds epochNow()
{
    return std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch());
}

std::string payload(std::string_view cmdId, int targetPct,
                    std::chrono::seconds issued, int ttlSec)
{
    return std::format(
        R"({{"cmd_id":"{}","op":"set_valve_position","target_pct":{},"issued_at":{},"ttl_sec":{}}})",
        cmdId, targetPct, issued.count(), ttlSec);
}

/* Викликається просто з мережевого колбеку: жодних затримок, жодних
   тривалих обчислень — лише фільтрація і передача наказу воркерові. */
void handleDownlink(std::string_view raw, cp::Actuator& actuator, cp::DedupRing& dedup)
{
    const auto parsed = cp::parseDownlink(raw);
    if (!parsed) {
        cp::publishNack(cp::describe(parsed.error()));
        return;
    }
    const cp::Downlink& cmd = *parsed;

    const auto now = epochNow();
    if (now > cmd.issuedAt + cmd.ttl) {
        /* Наказ пролежав довше, ніж дозволив оператор: за цей час стан
           установки міг змінитися, виконувати наосліп не можна. */
        cp::publishStatus(cmd.cmdId, "EXPIRED", 0, actuator.position(), cp::ErrCode::TtlExpired);
        return;
    }

    if (const auto seen = dedup.find(cmd.cmdId)) {
        cp::publishAck(cmd.cmdId, "ACK_DUPLICATE");
        cp::publishStatus(cmd.cmdId, seen->state, seen->progressPct, seen->valuePct, seen->err);
        return;
    }

    dedup.remember(cmd.cmdId, now);
    cp::publishAck(cmd.cmdId, "ACK_RECEIVED");      // фаза 1, до всякого руху

    if (!actuator.submit(cp::Actuator::Job{cmd.cmdId, cmd.targetPct})) {
        const int pos = actuator.position();
        cp::publishStatus(cmd.cmdId, "FAILED", 0, pos, cp::ErrCode::Busy);
        dedup.update(cmd.cmdId, cp::Outcome{"FAILED", 0, pos, cp::ErrCode::Busy});
    }
}

/* Другий потік: механіка стенда і швидкий цикл приводу. */
std::jthread spawnWorker(cp::Actuator& actuator, cp::Valve& valve,
                         std::chrono::steady_clock::time_point start)
{
    return std::jthread{[&actuator, &valve, start](const std::stop_token& stop) {
        auto uptime = [start] {
            return std::chrono::duration_cast<cp::Millis>(
                std::chrono::steady_clock::now() - start);
        };
        auto previous = uptime();
        while (!stop.stop_requested()) {
            std::this_thread::sleep_for(10ms);
            const auto now = uptime();
            valve.tick(now - previous);
            previous = now;
            actuator.poll(now);
        }
    }};
}

}  // namespace

int main()
{
    cp::Valve valve;
    cp::DedupRing dedup;
    const auto start = std::chrono::steady_clock::now();

    {
        cp::Actuator actuator{valve, dedup};
        auto worker = spawnWorker(actuator, valve, start);

        std::cout << "== 1. Звичайна команда: відкрити засувку ==\n";
        const std::string open = payload("6f21-open", 100, epochNow(), 60);
        handleDownlink(open, actuator, dedup);
        std::this_thread::sleep_for(900ms);

        std::cout << "== 2. Сервер не дочекався квитанції і повторив пакет ==\n";
        handleDownlink(open, actuator, dedup);
        std::this_thread::sleep_for(2s);

        std::cout << "== 3. Наказ пролежав довше за TTL ==\n";
        handleDownlink(payload("6f21-stale", 0, epochNow() - 300s, 5), actuator, dedup);
        std::this_thread::sleep_for(200ms);

        std::cout << "== 4. Вал заклинило: воркер сам закриває транзакцію ==\n";
        valve.setJammed(true);
        handleDownlink(payload("6f21-close", 0, epochNow(), 60), actuator, dedup);
        std::this_thread::sleep_for(6500ms);

        std::cout << "== 5. Просідання живлення посеред маневру ==\n";
        valve.setJammed(false);
        handleDownlink(payload("6f21-half", 40, epochNow(), 60), actuator, dedup);
        std::this_thread::sleep_for(400ms);
    }   // воркер зупинився, об'єкти зникли — це і є знеструмлення плати

    {
        cp::Actuator afterReset{valve, dedup};   // конструктор бачить незавершений хід
        auto worker = spawnWorker(afterReset, valve, start);
        std::this_thread::sleep_for(300ms);
    }

    std::cout << "== кінець ==\n";
    return 0;
}
