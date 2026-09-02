#pragma once

#include "modem_hal.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

/* Чорна скринька з'єднання: кільце переходів у пам'яті, що переживає
   знеструмлення. Кадр журналу їде на сервер першим же успішним сеансом. */
class BlackBox {
public:
    struct Record {
        std::uint32_t timestampMs{0};  /* Системний час моменту переходу */
        std::uint8_t fromState{0};     /* Початковий стан */
        std::uint8_t toState{0};       /* Новий стан */
        std::uint8_t eventId{0};       /* Подія, що викликала перехід */
        std::uint8_t retryCount{0};    /* Поточний лічильник спроб */
        std::int8_t rssiDbm{0};        /* Рівень сигналу в момент події (дБм) */
        std::uint16_t cmeErrorCode{0}; /* Останній числовий код CME/CMS ERROR */
        std::uint16_t voltageVbatMv{0}; /* Напруга живлення (мілівольти) */
        std::array<std::uint8_t, 2> reserved{}; /* Вирівнювання до 16 байтів */
    };

    static_assert(sizeof(Record) == 16, "запис журналу мусить лишатися 16-байтовим");

    static constexpr std::size_t kDepth = 32;
    static constexpr std::size_t kRecordSize = sizeof(Record);

    explicit BlackBox(ModemHal& hal); /* підіймає кільце зі збереженої пам'яті */
    ~BlackBox();                      /* журнал не гине разом з об'єктом */

    BlackBox(const BlackBox&) = delete;
    BlackBox& operator=(const BlackBox&) = delete;

    void record(std::uint8_t fromState, std::uint8_t toState, std::uint8_t eventId,
                std::uint8_t retryCount, std::int8_t rssiDbm, std::uint16_t cmeCode,
                std::uint16_t vbatMv);

    void flush(); /* запис у NV перед знеструмленням модема */

    /* Пакує найстаріші записи в кадр телеметрії. */
    [[nodiscard]] std::span<const std::byte> exportFrame(std::span<std::byte> out) const;

    /* Викидає підтверджені сервером записи (bytes = довжина кадру). */
    void markSent(std::size_t bytes);

    [[nodiscard]] std::size_t size() const noexcept { return m_nv.count; }

private:
    struct Store {
        std::uint32_t magic{0};
        std::uint8_t head{0};  /* куди ляже наступний запис */
        std::uint8_t count{0}; /* скільки записів чинні */
        std::uint16_t crc{0};
        std::array<Record, kDepth> records{};
    };

    [[nodiscard]] std::uint16_t computeCrc() const;
    void resetStore();

    ModemHal& m_hal;
    Store m_nv{};
};
