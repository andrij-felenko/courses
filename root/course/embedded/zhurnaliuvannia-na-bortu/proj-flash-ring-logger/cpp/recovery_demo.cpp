// Емуляція NOR Flash на хості й сценарії відмов.
//
// Модель кристала тримає дві фізичні властивості, на яких стоїть увесь формат:
// запис уміє лише гасити біти (побайтове AND), а стирання піднімає весь сектор
// у 0xFF. Плюс керовані відмови — так перевіряється поведінка, якої на столі
// не дочекаєшся: обрив живлення посеред кадру й сектор, що перестав стиратися.
//
// Збірка: c++ -std=c++23 record_codec.cpp ring_logger.cpp recovery_demo.cpp
// (rtos_logger.cpp сюди не входить — він потребує FreeRTOS).

#include <algorithm>
#include <array>
#include <bitset>
#include <cstdint>
#include <format>
#include <iostream>
#include <string_view>
#include <vector>

#include "flash_device.hpp"
#include "record_codec.hpp"
#include "ring_logger.hpp"
#include "staging_ring.hpp"

namespace {

int g_failures = 0;

void check(bool ok, std::string_view what)
{
    std::cout << std::format("{} {}\n", ok ? "[ok]  " : "[ЗБІЙ]", what);
    if (!ok) {
        ++g_failures;
    }
}

class SimulatedFlash final : public fl::FlashDevice {
public:
    SimulatedFlash() : memory_(fl::kSectorSize * fl::kSectorCount, std::byte{0xFF}) {}

    std::expected<void, fl::FlashError> read(std::uint32_t address,
                                             std::span<std::byte> destination) override
    {
        if (address + destination.size() > memory_.size()) {
            return std::unexpected(fl::FlashError::OutOfRange);
        }
        std::ranges::copy_n(memory_.begin() + static_cast<std::ptrdiff_t>(address),
                            static_cast<std::ptrdiff_t>(destination.size()), destination.begin());
        return {};
    }

    std::expected<void, fl::FlashError> write(std::uint32_t address,
                                              std::span<const std::byte> source) override
    {
        if (address + source.size() > memory_.size()) {
            return std::unexpected(fl::FlashError::OutOfRange);
        }
        if (writeFail_.test(address / fl::kSectorSize)) {
            return std::unexpected(fl::FlashError::Io);
        }
        for (std::size_t i = 0; i < source.size(); ++i) {
            memory_[address + i] &= source[i];  // одиницю в нуль можна, назад — ні
        }
        return {};
    }

    std::expected<void, fl::FlashError> eraseSector(std::uint32_t sectorAddress) override
    {
        const std::size_t idx = sectorAddress / fl::kSectorSize;
        if (idx >= fl::kSectorCount) {
            return std::unexpected(fl::FlashError::OutOfRange);
        }
        if (eraseFail_.test(idx)) {
            return std::unexpected(fl::FlashError::Io);
        }
        std::ranges::fill(std::span{memory_}.subspan(idx * fl::kSectorSize, fl::kSectorSize),
                          std::byte{0xFF});
        return {};
    }

    void degradeErase(std::size_t sector) { eraseFail_.set(sector); }
    void degradeWrite(std::size_t sector) { writeFail_.set(sector); }

    [[nodiscard]] std::span<const std::byte> image() const noexcept { return memory_; }

private:
    std::vector<std::byte> memory_;
    std::bitset<fl::kSectorCount> eraseFail_{};
    std::bitset<fl::kSectorCount> writeFail_{};
};

fl::SectorState sectorStateOf(const SimulatedFlash& flash, std::size_t idx)
{
    fl::SectorHeaderBytes raw{};
    std::ranges::copy(flash.image().subspan(idx * fl::kSectorSize, fl::kSectorHeaderSize),
                      raw.begin());
    return fl::SectorHeader::decode(raw).state;
}

// Скільки в усьому кристалі валідних кадрів із таким токеном; у lastPayload
// кладе перші чотири байти навантаження останнього знайденого.
std::uint32_t countToken(const SimulatedFlash& flash, std::uint32_t token,
                         std::uint32_t* lastPayload = nullptr)
{
    std::uint32_t found = 0;

    for (std::size_t sector = 0; sector < fl::kSectorCount; ++sector) {
        const std::span<const std::byte> body =
            flash.image().subspan(sector * fl::kSectorSize, fl::kSectorSize);

        fl::SectorHeaderBytes headerBytes{};
        std::ranges::copy(body.subspan(0, fl::kSectorHeaderSize), headerBytes.begin());
        if (fl::SectorHeader::decode(headerBytes).magic != fl::kSectorMagic) {
            continue;
        }

        std::size_t offset = fl::kSectorHeaderSize;
        while (offset + fl::kRecordHeaderSize + fl::kCrcSize <= fl::kSectorSize) {
            const auto record = fl::decodeRecord(body.subspan(offset, fl::kSectorSize - offset));
            if (!record) {
                break;
            }
            if (record->header.tokenId == token) {
                ++found;
                if (lastPayload != nullptr && record->payload.size() >= 4) {
                    *lastPayload = fl::getU32(record->payload);
                }
            }
            offset += record->header.length;
        }
    }
    return found;
}

std::array<std::byte, 4> payloadOf(std::uint32_t value)
{
    std::array<std::byte, 4> payload{};
    fl::putU32(payload, value);
    return payload;
}

// Пише кадри, доки логер не перейде в наступний сектор.
std::uint32_t fillUntilRotation(fl::RingLogger& logger, std::uint32_t& timestamp)
{
    const std::uint32_t start = logger.activeSector();
    std::uint32_t written = 0;

    while (logger.activeSector() == start) {
        if (!logger.append(fl::Level::Info, 7, timestamp, 0x2000u, payloadOf(timestamp))) {
            break;
        }
        ++timestamp;
        ++written;
    }
    return written;
}

constexpr std::uint32_t kRecordSize = fl::kRecordHeaderSize + 4 + fl::kCrcSize;  // 19 байтів
constexpr std::uint32_t kRecordsPerSector = (fl::kSectorSize - fl::kSectorHeaderSize) / kRecordSize;

void scenarioFreshStart()
{
    std::cout << "\n1. Чистий кристал: перший старт і перші записи\n";
    SimulatedFlash flash;
    fl::RingLogger logger{flash};

    check(logger.init().has_value(), "init на чистому кристалі");
    check(logger.activeSector() == 0, "активний сектор — нульовий");
    check(logger.writeOffset() == fl::kSectorHeaderSize, "покажчик стоїть одразу за заголовком");
    check(sectorStateOf(flash, 0) == fl::SectorState::Active, "сектор 0 позначено Active");

    check(logger.append(fl::Level::Info, 1, 1000, 0x1001u, payloadOf(120)).has_value(),
          "запис Info");
    check(logger.append(fl::Level::Warn, 2, 1050, 0x1002u, payloadOf(404)).has_value(),
          "запис Warn");
    check(logger.writeOffset() == fl::kSectorHeaderSize + 2 * kRecordSize,
          "покажчик просунувся на два кадри");
    check(countToken(flash, 0x1001u) == 1 && countToken(flash, 0x1002u) == 1,
          "обидва кадри читаються з валідною CRC");
}

void scenarioPowerCut()
{
    std::cout << "\n2. Знеструмлення посеред кадру й відновлення на старті\n";
    SimulatedFlash flash;
    fl::RingLogger logger{flash};
    static_cast<void>(logger.init());

    static_cast<void>(logger.append(fl::Level::Info, 1, 1000, 0x1001u, payloadOf(1)));
    static_cast<void>(logger.append(fl::Level::Warn, 2, 1050, 0x1002u, payloadOf(2)));

    const std::uint32_t cutOffset = logger.writeOffset();

    // Живлення зникає посеред Page Program: у Flash лягли перші 6 байтів
    // третього кадру — магічне число, довжина, рівень, модуль і початок мітки
    // часу. Ні тіла, ні CRC немає. Відтворюємо цей стан прямим записом.
    const fl::RecordHeader doomed{
        .length = 0,
        .level = fl::Level::Error,
        .moduleId = 3,
        .timestampMs = 1100,
        .tokenId = 0x1003u,
    };
    std::array<std::byte, fl::kMaxRecordSize> frame{};
    const auto encoded = fl::encodeRecord(doomed, payloadOf(3), frame);
    check(encoded.has_value() && encoded->size() == kRecordSize, "кадр зібрано");
    check(flash.write(cutOffset, encoded->subspan(0, 6)).has_value(),
          "у Flash лягли лише 6 байтів кадру");

    // Скидання мікроконтролера.
    fl::RingLogger rebooted{flash};
    check(rebooted.init().has_value(), "init після аварійного скидання");
    check(rebooted.activeSector() == 0, "активним лишився той самий сектор");
    check(rebooted.writeOffset() == cutOffset, "покажчик став рівно перед битим кадром");
    check(countToken(flash, 0x1003u) == 0, "недописаний кадр не зарахований як валідний");

    // Поверх обірваних байтів валідний кадр не ляже: NOR уміє лише гасити
    // біти. Логер побачить це на звірянні й піде в наступний сектор.
    check(rebooted.append(fl::Level::Info, 1, 1200, 0x1004u, payloadOf(4)).has_value(),
          "наступний запис пройшов");
    check(rebooted.activeSector() == 1, "сектор із бітим хвостом закрито, запис пішов у наступний");
    check(sectorStateOf(flash, 0) == fl::SectorState::Full, "сектор 0 позначено Full");
    check(countToken(flash, 0x1004u) == 1, "новий кадр читається");
}

void scenarioRotation()
{
    std::cout << "\n3. Заповнення сектора й ротація\n";
    SimulatedFlash flash;
    fl::RingLogger logger{flash};
    static_cast<void>(logger.init());

    std::uint32_t timestamp = 1;
    const std::uint32_t written = fillUntilRotation(logger, timestamp);

    // Останній із порахованих записів уже впав у новий сектор — саме він
    // і викликав ротацію, не помістившись у хвіст старого.
    check(written == kRecordsPerSector + 1, "сектор набито до останнього кадру, що влазить");
    check(logger.activeSector() == 1, "голова перейшла в сектор 1");
    check(sectorStateOf(flash, 0) == fl::SectorState::Full, "старий сектор закрито як Full");
    check(sectorStateOf(flash, 1) == fl::SectorState::Active, "новий сектор відкрито як Active");

    fl::SectorHeaderBytes first{};
    fl::SectorHeaderBytes second{};
    std::ranges::copy(flash.image().subspan(0, fl::kSectorHeaderSize), first.begin());
    std::ranges::copy(flash.image().subspan(fl::kSectorSize, fl::kSectorHeaderSize), second.begin());
    const auto h0 = fl::SectorHeader::decode(first);
    const auto h1 = fl::SectorHeader::decode(second);
    check(h1.seqNum == h0.seqNum + 1, "номер послідовності зріс на одиницю");
    check(h1.eraseCount == 1, "лічильник стирань нового сектора став одиницею");
}

void scenarioOverrun()
{
    std::cout << "\n4. Повний обіг кільця: хвіст витісняється\n";
    SimulatedFlash flash;
    fl::RingLogger logger{flash};
    static_cast<void>(logger.init());

    check(logger.tailSector() == 0, "спочатку хвіст стоїть на нульовому секторі");

    std::uint32_t timestamp = 1;
    for (std::size_t i = 0; i < fl::kSectorCount + 1; ++i) {
        static_cast<void>(fillUntilRotation(logger, timestamp));
    }

    check(logger.tailSector() == (logger.activeSector() + 1) % fl::kSectorCount,
          "хвіст стоїть одразу за головою — найстаріші дані затерто");

    const std::uint32_t head = logger.activeSector();
    const std::uint32_t tail = logger.tailSector();
    fl::RingLogger rebooted{flash};
    static_cast<void>(rebooted.init());
    check(rebooted.activeSector() == head, "після скидання голова знайдена там само");
    check(rebooted.tailSector() == tail, "після скидання хвіст знайдений там само");
}

void scenarioBadSector()
{
    std::cout << "\n5. Сектор перестав стиратися\n";
    SimulatedFlash flash;
    flash.degradeErase(1);

    fl::RingLogger logger{flash};
    static_cast<void>(logger.init());

    std::uint32_t timestamp = 1;
    static_cast<void>(fillUntilRotation(logger, timestamp));

    check(logger.activeSector() == 2, "дефектний сектор обійдено, голова стала в сектор 2");
    check(logger.badSectors().test(1), "сектор 1 занесено в маску дефектних");

    std::uint32_t reported = 0xFFFFFFFFu;
    check(countToken(flash, fl::kTokenBadSector, &reported) == 1,
          "у журналі з'явився службовий запис про дефект");
    check(reported == 1, "у навантаженні службового запису — номер битого сектора");

    static_cast<void>(fillUntilRotation(logger, timestamp));
    check(logger.activeSector() == 3, "після дефектного сектора ротація йде своїм ходом");
}

void scenarioUpload()
{
    std::cout << "\n6. Вивантаження пачки й підтвердження від сервера\n";
    SimulatedFlash flash;
    fl::RingLogger logger{flash};
    static_cast<void>(logger.init());

    std::uint32_t timestamp = 1;
    static_cast<void>(fillUntilRotation(logger, timestamp));

    std::vector<std::byte> buffer(fl::kSectorSize);
    const auto batch = logger.readBatch(buffer);
    check(batch.has_value(), "пачка вичитана");
    if (!batch) {
        return;
    }
    check(batch->sector == 0, "віддано найстаріший заповнений сектор");
    check(batch->records == kRecordsPerSector, "у пачці всі кадри сектора");

    // Перевіряємо, що віддане справді розбирається — саме це робитиме сервер.
    std::size_t parsed = 0;
    std::size_t offset = 0;
    while (offset < batch->bytes.size()) {
        const auto record = fl::decodeRecord(batch->bytes.subspan(offset));
        if (!record) {
            break;
        }
        offset += record->header.length;
        ++parsed;
    }
    check(parsed == batch->records, "усі кадри пачки проходять перевірку CRC");

    check(logger.commitTail(batch->sector).has_value(), "сервер підтвердив пачку");
    check(sectorStateOf(flash, 0) == fl::SectorState::Dirty, "сектор позначено Dirty");
    check(logger.tailSector() == 1, "хвіст просунувся до наступного сектора");

    const auto empty = logger.readBatch(buffer);
    check(!empty && empty.error() == fl::LoggerError::NothingToUpload,
          "більше заповнених секторів немає — активний не віддається");
}

void scenarioIsrQueue()
{
    std::cout << "\n7. Черга переривань і фонове перенесення у Flash\n";
    SimulatedFlash flash;
    fl::RingLogger logger{flash};
    static_cast<void>(logger.init());

    fl::StagingRing<fl::kStageCapacity> stage;

    for (std::uint16_t i = 0; i < 3; ++i) {
        const fl::StagedRecord record{
            .level = fl::Level::Debug,
            .moduleId = 9,
            .arg = static_cast<std::uint16_t>(100 + i),
            .timestampMs = 2000u + i,
            .tokenId = 0x3001u,
        };
        check(stage.push(record), "кадр покладено в чергу з переривання");
    }

    check(fl::drain(stage, logger) == 3, "фонова задача перенесла всі три кадри");
    check(countToken(flash, 0x3001u) == 3, "кадри лежать у Flash");

    // Переповнення: черга тримає kStageCapacity кадрів, решта гине.
    for (std::uint32_t i = 0; i < fl::kStageCapacity + 8; ++i) {
        const fl::StagedRecord record{
            .level = fl::Level::Trace,
            .moduleId = 9,
            .arg = static_cast<std::uint16_t>(i),
            .timestampMs = 3000u + i,
            .tokenId = 0x3002u,
        };
        static_cast<void>(stage.push(record));
    }

    check(fl::drain(stage, logger) == fl::kStageCapacity,
          "перенесено рівно стільки, скільки вмістила черга");

    std::uint32_t dropped = 0;
    check(countToken(flash, fl::kTokenIsrDrops, &dropped) == 1,
          "втрату кадрів визнано записом Warn");
    check(dropped == 8, "у записі стоїть точна кількість утрачених кадрів");
}

}  // namespace

int main()
{
    scenarioFreshStart();
    scenarioPowerCut();
    scenarioRotation();
    scenarioOverrun();
    scenarioBadSector();
    scenarioUpload();
    scenarioIsrQueue();

    std::cout << std::format("\nЗбоїв: {}\n", g_failures);
    return g_failures == 0 ? 0 : 1;
}
