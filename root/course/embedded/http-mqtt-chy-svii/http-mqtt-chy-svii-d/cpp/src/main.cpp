// main.cpp — цикл вузла: прокинувся, зміряв, вистрілив датаграму, заснув.
//
// Збірка:
//   c++ -std=c++23 -O2 -Wall -Wextra -o node    main.cpp codec.cpp uplink.cpp
//   c++ -std=c++23 -O2 -Wall -Wextra -o gateway gateway.cpp codec.cpp
//
// Запуск:  ./gateway 9000  і в іншому терміналі  ./node 127.0.0.1 9000
//
// На мікроконтролері замість main() тут була б функція, яку викликає
// пробудження від RTC, а замість виходу з main() — виклик сну.
#include <cstdint>
#include <cstdlib>
#include <ctime>
#include <format>
#include <fstream>
#include <iostream>
#include <string>

#include "uplink.hpp"

namespace {

constexpr const char* kSpoolPath = "node.spool";
constexpr const char* kSeqPath   = "node.seq";

// Номер кадру мусить пережити перезавантаження, інакше після скидання вузол
// почне з нуля і сервер вважатиме свіжі виміри дублікатами.
// У прошивці це запис у NVS, тут — два байти у файлі.
std::uint16_t loadSeq()
{
    std::ifstream file{kSeqPath, std::ios::binary};
    if (!file) {
        return 0;
    }
    std::uint16_t seq = 0;
    file.read(reinterpret_cast<char*>(&seq), sizeof seq);
    return file.gcount() == sizeof seq ? seq : std::uint16_t{0};
}

void storeSeq(std::uint16_t seq)
{
    std::ofstream file{kSeqPath, std::ios::binary | std::ios::trunc};
    if (!file) {
        std::cerr << "node: лічильник не збережено\n";
        return;
    }
    file.write(reinterpret_cast<const char*>(&seq), sizeof seq);
}

// У прошивці тут читання SHT4x по I²C і напруги батареї з АЦП.
// Щоб приклад ішов на ПК, числа беремо детерміновані, але правдоподібні.
telemetry::Sample measure()
{
    const auto now = std::time(nullptr);
    const long minute = static_cast<long>(now % 3600) / 60;   // 0..59

    return telemetry::Sample{
        .timestamp   = static_cast<std::uint32_t>(now),
        .temperature = static_cast<std::int16_t>(1800 + minute * 10),
        .humidity    = static_cast<std::uint16_t>(4000 + (59 - minute) * 20),
        .vbat_mv     = static_cast<std::uint16_t>(3000 - (now % 600) / 10),
    };
}

std::string celsius(std::int16_t hundredths)
{
    return std::format("{}.{:02}", hundredths / 100, std::abs(hundredths % 100));
}

}  // namespace

int main(int argc, char** argv)
{
    const std::string host = argc > 1 ? argv[1] : "127.0.0.1";
    const std::string port = argc > 2 ? argv[2] : "9000";

    auto socket = telemetry::UdpSocket::to(host, port);
    if (!socket) {
        std::cerr << std::format("node: {}:{} — {}\n", host, port,
                                 telemetry::describe(socket.error()));
        return 1;
    }

    telemetry::Uplink uplink{std::move(*socket), kSpoolPath, loadSeq()};

    // Спершу віддаємо борги: модем уже увімкнений, і кожен відкладений кадр
    // коштує тепер лише свої 16 байтів, а не окремого пробудження.
    if (const auto replayed = uplink.flushSpool(); replayed > 0) {
        std::cout << std::format("віддано зі спулу: {} кадр(ів)\n", replayed);
    }

    const auto sample = measure();
    const bool acked = uplink.send(sample);
    const auto seq = static_cast<unsigned>(uplink.seq() - 1);

    if (acked) {
        std::cout << std::format("кадр #{} підтверджено: {} °C, {}.{:02} %, {} мВ\n",
                                 seq, celsius(sample.temperature),
                                 sample.humidity / 100, sample.humidity % 100,
                                 sample.vbat_mv);
    } else {
        std::cout << std::format("кадр #{} відкладено у спул\n", seq);
    }

    storeSeq(uplink.seq());

    // Головне число цієї теми: скільки мілісекунд передавач мусив жити.
    // Для HTTPS-сеансу з нуля тут було б понад тисячу.
    std::cout << std::format("передавач був потрібен {} мс\n",
                             uplink.transmitTime().count());

    return acked ? 0 : 1;
}
