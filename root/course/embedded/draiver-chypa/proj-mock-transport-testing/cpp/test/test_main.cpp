// test_main.cpp — набір модульних тестів драйвера, що біжить на ПК.
//
// Збірка й запуск нативним компілятором, без жодної плати:
//     c++ -std=c++23 -Wall -Wextra -Iinclude test/test_main.cpp -o chip_tests
//     ./chip_tests
// Ненульовий код повернення — сигнал для конвеєра неперервної інтеграції.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <print>
#include <random>
#include <source_location>
#include <string_view>

#include "chip/accelerometer.hpp"
#include "chip/registers.hpp"
#include "mock_transport.hpp"

using chip::Error;
using chip::Range;
using chip::testing::MockTransport;
namespace reg = chip::reg;

// Мок мусить задовольняти той самий концепт, що й справжня шина: інакше
// тест перевіряв би інший драйвер, ніж поїде в прошивку.
static_assert(chip::Transport<MockTransport>);

namespace {

unsigned g_checks   = 0;
unsigned g_failures = 0;

void check(bool ok,
           std::string_view expression,
           const std::source_location location = std::source_location::current())
{
    ++g_checks;
    if (!ok) {
        ++g_failures;
        std::println(stderr, "    [FAIL] рядок {}: {}", location.line(), expression);
    }
}

#define CHECK(cond) check((cond), #cond)

bool near(float value, float expected, float epsilon)
{
    return std::fabs(value - expected) <= epsilon;
}

// Кожен тест починає з чистого кремнію: спільний стан між тестами — це
// найдешевший спосіб дістати набір, що зеленіє лише в одному порядку.
struct Fixture {
    MockTransport                   mock{};
    chip::Accelerometer<MockTransport> sensor{mock};

    void initialize() { CHECK(sensor.init().has_value()); }
};

// --- Тест 1: ініціалізація та конфігурація регістрів ------------------------
void testInitConfiguresRegisters()
{
    Fixture fixture;
    const unsigned before = g_failures;

    CHECK(fixture.sensor.init().has_value());
    CHECK(fixture.sensor.initialized());

    const auto& log = fixture.mock.writeLog();
    CHECK(log.size() >= 2);
    // Ідентифікатор читають до першого запису — номер транзакції це доводить.
    CHECK(!log.empty() && log.front().seq > 1);

    const auto ctrl1 = fixture.mock.lastWrite(reg::Ctrl1);
    const auto ctrl4 = fixture.mock.lastWrite(reg::Ctrl4);
    CHECK(ctrl1.has_value());
    CHECK(ctrl4.has_value());

    if (ctrl1 && ctrl4) {
        CHECK((*ctrl1 & reg::Ctrl1AxesMask) == reg::Ctrl1AxesMask);
        CHECK(((*ctrl1 & reg::Ctrl1OdrMask) >> reg::Ctrl1OdrShift) == reg::Odr100Hz);
        CHECK((*ctrl1 & reg::Ctrl1LowPower) == 0);

        // BDU обов'язковий: без нього між читанням молодшого й старшого байта
        // чип встигає підкласти новий відлік, і виходить каліка з двох різних.
        CHECK((*ctrl4 & reg::Ctrl4Bdu) != 0);
        CHECK((*ctrl4 & reg::Ctrl4HighRes) != 0);
        CHECK((*ctrl4 & reg::Ctrl4FsMask) == 0); // ±2 g за замовчуванням
    }

    // Жоден байт конфігурації не пішов у регістр лише для читання.
    for (const auto& entry : log) {
        CHECK(entry.applied);
    }

    std::println("[{}] Тест 1: ініціалізація та налаштування регістрів",
                 g_failures == before ? "PASS" : "FAIL");
}

// --- Тест 2: чужий чип і мовчазна шина --------------------------------------
void testRejectsForeignChip()
{
    const unsigned before = g_failures;

    for (const std::uint8_t badId : {std::uint8_t{0x00}, std::uint8_t{0xFF},
                                     std::uint8_t{0x32}}) {
        Fixture fixture;
        fixture.mock.poke(reg::WhoAmI, badId);

        const auto result = fixture.sensor.init();
        CHECK(!result.has_value());
        CHECK(!result && result.error() == Error::DeviceNotFound);
        CHECK(!fixture.sensor.initialized());
        // Ключове: у чужий кремній не пішло жодного байта конфігурації.
        CHECK(fixture.mock.writeLog().empty());
    }

    {
        Fixture fixture;
        fixture.mock.setDeviceAbsent(true);
        const auto result = fixture.sensor.init();
        CHECK(!result && result.error() == Error::Comm);

        // Робота з неініціалізованим драйвером заборонена.
        const auto sample = fixture.sensor.readSi();
        CHECK(!sample && sample.error() == Error::NotInitialized);
        const auto ranged = fixture.sensor.setRange(Range::G4);
        CHECK(!ranged && ranged.error() == Error::NotInitialized);
    }

    std::println("[{}] Тест 2: захист від чужого чипа й мовчазної шини",
                 g_failures == before ? "PASS" : "FAIL");
}

// --- Тест 3: точність переходу до SI ----------------------------------------
void testSiConversion()
{
    Fixture fixture;
    fixture.initialize();
    const unsigned before = g_failures;

    // ±2 g: половина шкали — це рівно 1 g.
    fixture.mock.setRawXyz(0, 0, 16384);
    if (const auto sample = fixture.sensor.readSi(); sample) {
        CHECK(near(sample->x, 0.0F, 0.001F));
        CHECK(near(sample->y, 0.0F, 0.001F));
        CHECK(near(sample->z, chip::kGravity, 0.001F));
    } else {
        CHECK(false);
    }

    // Від'ємні коди в доповняльному коді: знак мусить поширитися з 16 біт.
    fixture.mock.setRawXyz(-16384, 32767, -32768);
    if (const auto sample = fixture.sensor.readSi(); sample) {
        CHECK(near(sample->x, -chip::kGravity, 0.001F));
        CHECK(sample->y > 0.0F);
        CHECK(near(sample->z, -2.0F * chip::kGravity, 0.001F));
    } else {
        CHECK(false);
    }

    // Зміна діапазону подвоює ціну відліку й не чіпає інших бітів CTRL4.
    CHECK(fixture.sensor.setRange(Range::G4).has_value());
    if (const auto ctrl4 = fixture.mock.lastWrite(reg::Ctrl4); ctrl4) {
        CHECK((*ctrl4 & reg::Ctrl4Bdu) != 0);
        CHECK((*ctrl4 & reg::Ctrl4HighRes) != 0);
        CHECK(((*ctrl4 & reg::Ctrl4FsMask) >> reg::Ctrl4FsShift) ==
              static_cast<std::uint8_t>(Range::G4));
    } else {
        CHECK(false);
    }

    fixture.mock.setRawXyz(0, 0, 16384);
    if (const auto sample = fixture.sensor.readSi(); sample) {
        CHECK(near(sample->z, 2.0F * chip::kGravity, 0.002F));
    } else {
        CHECK(false);
    }

    // Зворотний шлях: генератор задає фізичну величину, драйвер має її
    // повернути. Синусоїда по осі X — модель столу, що вібрує.
    CHECK(fixture.sensor.setRange(Range::G8).has_value());
    for (int step = 0; step < 16; ++step) {
        const float g = 3.0F * std::sin(static_cast<float>(step) * 0.4F);
        fixture.mock.setAcceleration(Range::G8, g, 0.0F, 1.0F);

        const auto sample = fixture.sensor.readSi();
        CHECK(sample.has_value());
        if (sample) {
            CHECK(near(sample->x, g * chip::kGravity, 0.01F));
            CHECK(near(sample->z, chip::kGravity, 0.01F));
        }
    }

    std::println("[{}] Тест 3: точність переходу до м/с² і зміна діапазону",
                 g_failures == before ? "PASS" : "FAIL");
}

// --- Тест 4: повтори спроб і обрив передачі ---------------------------------
void testRetriesOnTransientFaults()
{
    const unsigned before = g_failures;
    const chip::RetryPolicy policy{.maxRetries = 3, .baseDelay = std::chrono::milliseconds{1}};

    {
        MockTransport mock;
        chip::Accelerometer<MockTransport> sensor{mock, policy};
        CHECK(sensor.init().has_value());

        // Дві поспіль невдачі — третя спроба вдала.
        mock.setRawXyz(0, 0, 16384);
        mock.injectReadFailures(2);
        const auto sample = sensor.readSi();
        CHECK(sample.has_value());
        if (sample) {
            CHECK(near(sample->z, chip::kGravity, 0.001F));
        }

        // Завада довша за політику повторів — драйвер чесно здається.
        mock.setRawXyz(0, 0, 16384);
        mock.injectReadFailures(10);
        const auto failed = sensor.readSi();
        CHECK(!failed && failed.error() == Error::Comm);
        CHECK(mock.pendingReadFailures() == 10 - (policy.maxRetries + 1));

        // Збій на записі теж повторюється: конфігурація не має губитися.
        mock.injectWriteFailures(2);
        CHECK(sensor.setRange(Range::G16).has_value());
        CHECK(sensor.range() == Range::G16);
    }

    {
        // Обрив пакетного читання на третьому байті: половина буфера — сміття,
        // і драйвер зобов'язаний повернути помилку, а не «майже правильні» осі.
        Fixture fixture;
        fixture.initialize();
        fixture.mock.setRawXyz(1000, 2000, 3000);
        fixture.mock.breakReadAtByte(3);

        const auto sample = fixture.sensor.readSi();
        CHECK(!sample && sample.error() == Error::Comm);
    }

    std::println("[{}] Тест 4: повтори спроб і обрив передачі",
                 g_failures == before ? "PASS" : "FAIL");
}

// --- Тест 5: прапорець готовності даних -------------------------------------
void testDataReadyFlag()
{
    Fixture fixture;
    fixture.initialize();
    const unsigned before = g_failures;

    // Одразу після ініціалізації нового відліку ще нема.
    const auto empty = fixture.sensor.readSi();
    CHECK(!empty && empty.error() == Error::NoData);

    fixture.mock.setRawXyz(0, 0, 16384);
    CHECK(fixture.sensor.readSi().has_value());

    // Відлік забрали — прапорець згас, повторне читання дає NoData, а не
    // тихо той самий байт удруге.
    const auto again = fixture.sensor.readSi();
    CHECK(!again && again.error() == Error::NoData);

    // Не забраний вчасно відлік лишає слід перезапису в STATUS.
    fixture.mock.setRawXyz(0, 0, 16384);
    fixture.mock.setRawXyz(0, 0, 8192);
    CHECK((fixture.mock.peek(reg::Status) & reg::StatusZyxor) != 0);

    std::println("[{}] Тест 5: облік готовності й перезапису даних",
                 g_failures == before ? "PASS" : "FAIL");
}

// --- Тест 6: стійкість математики до сміття на шині -------------------------
void testFuzzConversion()
{
    Fixture fixture;
    fixture.initialize();
    const unsigned before = g_failures;

    std::mt19937 rng{0xC0FFEEU}; // детермінований засів: збій відтворюваний
    std::uniform_int_distribution<int> byte{0, 255};
    std::uniform_int_distribution<int> small{0, 7};

    const float limit = static_cast<float>(fullScaleG(fixture.sensor.range())) *
                        chip::kGravity;
    unsigned accepted = 0;

    for (unsigned i = 0; i < 200000; ++i) {
        for (std::uint8_t address = reg::OutXL; address <= reg::OutZH; ++address) {
            fixture.mock.poke(address, static_cast<std::uint8_t>(byte(rng)));
        }
        fixture.mock.poke(reg::Status, static_cast<std::uint8_t>(byte(rng)));
        fixture.mock.injectReadFailures(static_cast<unsigned>(small(rng) & 0x3));
        fixture.mock.breakReadAtByte(static_cast<std::size_t>(small(rng)));

        const auto sample = fixture.sensor.readSi();
        if (!sample) {
            CHECK(sample.error() == Error::NoData || sample.error() == Error::Comm);
            continue;
        }
        ++accepted;

        // Жодна комбінація байтів не має дати ні NaN, ні виходу за шкалу.
        CHECK(std::isfinite(sample->x) && std::isfinite(sample->y) &&
              std::isfinite(sample->z));
        CHECK(std::fabs(sample->x) <= limit + 0.001F);
        CHECK(std::fabs(sample->y) <= limit + 0.001F);
        CHECK(std::fabs(sample->z) <= limit + 0.001F);

        if (g_failures != before) {
            break; // не топимо консоль тисячами однакових рядків
        }
    }

    CHECK(accepted > 0); // набір, що жодного разу не дійшов до мети, — брехня
    std::println("[{}] Тест 6: {} випадкових станів шини без NaN і виходу за шкалу",
                 g_failures == before ? "PASS" : "FAIL", accepted);
}

} // namespace

int main()
{
    std::println("=== Модульні тести драйвера на моці (без плати) ===");

    testInitConfiguresRegisters();
    testRejectsForeignChip();
    testSiConversion();
    testRetriesOnTransientFaults();
    testDataReadyFlag();
    testFuzzConversion();

    std::println("\nПеревірок: {}, невдалих: {}", g_checks, g_failures);
    if (g_failures != 0) {
        std::println(">>> НАБІР ПРОВАЛЕНО <<<");
        return 1;
    }
    std::println(">>> Усі перевірки пройдено <<<");
    return 0;
}
