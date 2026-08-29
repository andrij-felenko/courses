// main.cpp — прогін життєвих сценаріїв менеджера на моделі Flash.
#include "cfg/flash.hpp"
#include "cfg/manager.hpp"

#include <format>
#include <iostream>

namespace {

using namespace cfg;

// Кладемо в сектор запис старої схеми — так виглядає Flash приладу,
// що тільки-но прийняв прошивку v2.0 по повітрю.
void seed_legacy_v1_record(Flash& flash, std::size_t slot, std::uint32_t seq)
{
    PayloadV1 v1{};
    assign(v1.wifi_ssid, "Field_AP_17");
    assign(v1.wifi_pass, "old-secret");
    v1.broker_ip = {10, 0, 1, 5};
    v1.report_interval_s = 30;

    const Header hdr{
        .magic           = kMagic,
        .schema_version  = kSchemaV1,
        .flags           = 0,
        .sequence_number = seq,
        .payload_len     = static_cast<std::uint16_t>(sizeof(PayloadV1)),
        .reserved        = 0,
        .crc32_value     = crc32(raw_bytes(v1)),
    };

    flash.erase(slot);
    (void)flash.program(slot, sizeof(Header), raw_bytes(v1));
    (void)flash.program(slot, 0, raw_bytes(hdr));
}

void show(const Manager& manager, std::string_view tag)
{
    const auto& c = manager.live();
    std::cout << std::format("  {}: {}:{} tls={} звіт={} с таймаут={} с (Slot {}, seq={})\n",
                             tag, view(c.broker_host), c.broker_port, c.tls_enable,
                             c.report_interval_s, c.conn_timeout_s,
                             manager.active_slot() == 0 ? 'A' : 'B', manager.sequence());
}

bool boot(Manager& manager, std::string_view tag)
{
    if (auto started = manager.initialize(); !started) {
        std::cerr << std::format("  старт не вдався: {}\n", describe(started.error()));
        return false;
    }
    show(manager, tag);
    return true;
}

}  // namespace

int main()
{
    Flash flash;
    Manager manager{flash};

    std::cout << "== Холодний старт після конвеєра ==\n";
    if (!boot(manager, "заводський профіль")) {
        return 1;
    }

    std::cout << "\n== Старт прошивки v2.0 поверх запису схеми v1 ==\n";
    flash.wipe();
    seed_legacy_v1_record(flash, 0, 7);
    if (!boot(manager, "після міграції")) {
        return 1;
    }

    std::cout << "\n-- Тест 1: суперечливі параметри --\n";
    auto bad = manager.live();
    bad.report_interval_s = 60;
    bad.conn_timeout_s    = 10;
    if (auto trial = manager.start_trial(bad); !trial) {
        std::cout << std::format("  відхилено: {}\n", describe(trial.error()));
    } else {
        std::cout << "  ЗБІЙ ТЕСТУ: суперечливий кандидат пройшов валідацію\n";
    }

    std::cout << "\n-- Тест 2: недосяжний брокер, випробування добігає таймауту --\n";
    auto unreachable = manager.live();
    assign(unreachable.broker_host, "broken-server.invalid");
    unreachable.report_interval_s = 30;
    unreachable.conn_timeout_s    = 180;
    if (manager.start_trial(unreachable)) {
        show(manager, "у випробуванні");
        for (std::uint32_t sec = 0; sec < kTrialTimeoutS; ++sec) {
            manager.tick_1hz();   // handshake так і не стався
        }
        std::cout << std::format("  випробування активне: {}\n", manager.trial_active() ? "так" : "ні");
        show(manager, "після відкату");
    }

    std::cout << "\n-- Тест 3: валідний кандидат і підтверджений сеанс --\n";
    auto good = manager.live();
    assign(good.broker_host, "prod-mqtt.example.net");
    good.broker_port = 8883;
    if (manager.start_trial(good)) {
        std::cout << "  TLS піднявся, брокер відповів PINGRESP — фіксуємо\n";
        if (auto committed = manager.confirm_commit(); committed) {
            show(manager, "активний профіль");
        } else {
            std::cout << std::format("  фіксація не вдалася: {}\n", describe(committed.error()));
        }
    }

    std::cout << "\n== Перезавантаження з тим, що лежить у Flash ==\n";
    if (!boot(manager, "після перезавантаження")) {
        return 1;
    }
    return 0;
}
