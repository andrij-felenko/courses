#include <cstdint>
#include <format>
#include <iostream>
#include <random>
#include <span>
#include <string>
#include <string_view>
#include <vector>

#include "frame.hpp"
#include "receiver.hpp"

namespace {

// Зерно фіксоване, тож «ефірний шум» при кожному запуску той самий
// і числа в кінці відтворювані.
std::mt19937 gAir{0x2DD4A55Au};
std::bernoulli_distribution gNoise{0.5};

std::vector<std::uint8_t> asBytes(std::string_view text)
{
    return std::vector<std::uint8_t>(text.begin(), text.end());
}

void hexdump(std::string_view tag, std::span<const std::uint8_t> data)
{
    std::string line = std::format("{} ({} Б):", tag, data.size());
    for (const std::uint8_t byte : data) {
        line += std::format(" {:02X}", byte);
    }
    std::cout << line << '\n';
}

// Ефір: спершу трохи шуму, далі кадр біт за бітом, старшим уперед.
void airSend(radio::BitReceiver& rx, std::span<const std::uint8_t> frame, int noiseBits)
{
    for (int i = 0; i < noiseBits; ++i) {
        rx.pushBit(gNoise(gAir));
    }
    for (const std::uint8_t byte : frame) {
        rx.pushByteMsbFirst(byte);
    }
}

// Та сама передача, але з переставленим порядком бітів у байті.
void airSendLsbFirst(radio::BitReceiver& rx, std::span<const std::uint8_t> frame)
{
    for (const std::uint8_t byte : frame) {
        for (int bit = 0; bit < 8; ++bit) {
            rx.pushBit(((byte >> bit) & 1u) != 0);
        }
    }
}

} // namespace

int main()
{
    const auto payload = asBytes("TELEMETRY:BAT=3.81V");

    const auto built = radio::buildFrame(payload);
    if (!built) {
        std::cerr << std::format("кадр не зібрано: {}\n", radio::describe(built.error()));
        return 1;
    }
    const std::vector<std::uint8_t>& frame = *built;
    hexdump("кадр в ефір", frame);

    radio::BitReceiver rx;

    // 1. Нормальний прийом. Перед кадром 13 бітів шуму — число навмисно не
    //    кратне восьми: вирівнювання дає корелятор, а не якась межа в потоці.
    airSend(rx, frame, 13);
    if (const auto packet = rx.pop()) {
        std::cout << std::format("1) прийнято {} Б: {}\n", packet->size(),
                                 std::string(packet->begin(), packet->end()));
    } else {
        std::cout << "1) кадр не прийнято\n";
    }

    // 2. Один перевернутий біт у тілі кадру — CRC не сходиться.
    auto broken = frame;
    broken[radio::kPreambleBytes + 2 + 3] ^= 0x08;
    airSend(rx, broken, 7);
    std::cout << std::format("2) помилок CRC: {}, кадр у FIFO: {}\n",
                             rx.stats().crcErrors,
                             rx.pop().has_value() ? "є" : "немає");

    // 3. FIFO глибиною два: шлемо три кадри поспіль і не вичитуємо жодного.
    rx.flush();
    for (int i = 0; i < 3; ++i) {
        airSend(rx, frame, 5);
    }
    std::cout << std::format("3) переповнення FIFO: {}, втрачено кадрів: {}\n",
                             rx.overrun() ? "так" : "ні", rx.stats().overruns);
    rx.flush(); // CMD_FLUSHRX — без нього приймач так і стоятиме

    // 4. Той самий кадр, але біти в байті йдуть молодшим першим: візерунок
    //    синхрослова розсипається, корелятор мовчить.
    const auto syncsBefore = rx.stats().syncs;
    airSendLsbFirst(rx, frame);
    std::cout << std::format("4) LSB first: спрацювань корелятора {}\n",
                             rx.stats().syncs - syncsBefore);

    // 5. Порожній ефір: 2 млн бітів шуму — це близько 8 с на 250 кбіт/с.
    //    Детектор преамбули зводиться десятки разів, але корелятор за свої
    //    короткі вікна майже ніколи не знаходить синхрослова.
    radio::BitReceiver noiseRx;
    for (int i = 0; i < 2'000'000; ++i) {
        noiseRx.pushBit(gNoise(gAir));
    }
    const auto& s = noiseRx.stats();
    std::cout << std::format("5) шум: преамбул {}, синхрослів {}, брак довжини {}, кадрів {}\n",
                             s.arms, s.syncs, s.lengthErrors, s.frames);
    return 0;
}
