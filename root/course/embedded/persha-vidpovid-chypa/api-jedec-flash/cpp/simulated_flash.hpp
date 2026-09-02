#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>

#include "spi_link.hpp"

namespace flash {

/* Симулятор 128-Мбітного кристала SPI NOR: рівно стільки поведінки, скільки
   треба, щоб драйвер зустрів усі три аномалії розділу 5 — кристал, залишений
   попередньою прошивкою в QPI, активний цикл стирання й частотну межу
   опкоду 0x9F. */
class SimulatedFlash final : public SpiLink {
public:
    static constexpr unsigned kSourceHz = 80'000'000;  /* генератор периферії SPI */
    static constexpr unsigned kIdMaxHz  = 50'000'000;  /* межа опкоду 0x9F */
    static constexpr std::chrono::milliseconds kTick{5};        /* крок годинника */
    static constexpr std::chrono::milliseconds kEraseUntil{120};

    SimulatedFlash() { build_rom(); }

    unsigned set_clock(unsigned hz) override
    {
        const unsigned div = std::max(1U, (kSourceHz + std::max(1U, hz) - 1) / std::max(1U, hz));
        clock_ = kSourceHz / div;  /* дільник округляє частоту вниз */
        return clock_;
    }

    [[nodiscard]] unsigned clock() const noexcept override { return clock_; }

    [[nodiscard]] std::chrono::milliseconds now() override
    {
        now_ += kTick;  /* кожен запит часу просуває симульований годинник */
        return now_;
    }

    void transfer(std::span<const std::uint8_t> tx, std::span<std::uint8_t> rx) override
    {
        const std::size_t ticks = std::max(tx.size(), rx.size());
        for (std::size_t i = 0; i < ticks; ++i) {
            write_byte(i < tx.size() ? tx[i] : std::uint8_t{0});
            const std::uint8_t v = read_byte();
            if (i < rx.size()) {
                rx[i] = v;
            }
        }
    }

    void quad_write(std::span<const std::uint8_t> tx) override
    {
        for (std::uint8_t b : tx) {
            if (qpi_ && b == 0xFF) {
                qpi_ = false;  /* єдина команда, яку кристал у QPI розуміє */
            }
        }
    }

protected:
    void select() override
    {
        stage_ = Stage::Opcode;
        resp_ = Resp::Idle;
        addr_ = 0;
        addr_bytes_ = 0;
        cursor_ = 0;
        id_index_ = 0;
    }

    void release() noexcept override
    {
        stage_ = Stage::Opcode;
        resp_ = Resp::Idle;
    }

private:
    enum class Stage { Opcode, Address, Dummy, Data };
    enum class Resp { Idle, Id, Status, Rom, Zero };

    /* Паспорт: Winbond, тип 0x40, код ємності 0x18 = 2^24 = 16 МБ. */
    static constexpr std::array<std::uint8_t, 3> kId{0xEF, 0x40, 0x18};

    [[nodiscard]] bool busy() const noexcept { return now_ < kEraseUntil; }

    static void put32(std::span<std::uint8_t> dst, std::uint32_t v)
    {
        dst[0] = static_cast<std::uint8_t>(v);
        dst[1] = static_cast<std::uint8_t>(v >> 8);
        dst[2] = static_cast<std::uint8_t>(v >> 16);
        dst[3] = static_cast<std::uint8_t>(v >> 24);
    }

    /* Часи стирання пакуються по 7 бітів: лічильник і одиниця виміру. */
    static constexpr std::uint32_t erase_time(std::uint32_t count, std::uint32_t units)
    {
        return ((units & 3U) << 5) | (count & 0x1FU);
    }

    void build_rom()
    {
        rom_.fill(0xFF);
        /* Заголовок SFDP: сигнатура, ревізія 1.6 (JESD216B), один заголовок параметрів. */
        rom_[0] = 'S'; rom_[1] = 'F'; rom_[2] = 'D'; rom_[3] = 'P';
        rom_[4] = 0x06; rom_[5] = 0x01; rom_[6] = 0x00; rom_[7] = 0xFF;
        /* Заголовок базової таблиці: ID 0xFF00, 16 подвійних слів, вказівник 0x000080. */
        rom_[8] = 0x00; rom_[9] = 0x06; rom_[10] = 0x01; rom_[11] = 16;
        rom_[12] = static_cast<std::uint8_t>(kTableOffset);
        rom_[13] = 0x00; rom_[14] = 0x00; rom_[15] = 0xFF;

        const auto dword = [this](std::size_t index) {
            return std::span{rom_}.subspan(kTableOffset + index * 4, 4);
        };
        /* Значення за форматом JESD216B, як у типового 128-Мбітного кристала. */
        put32(dword(0), 0xFFF9'20E5U);  /* 4К-стирання опкодом 0x20, трибайтова адреса, є 1-1-4 і 1-4-4 */
        put32(dword(1), 0x07FF'FFFFU);  /* щільність: 0x07FFFFFF + 1 = 134 217 728 біт = 16 МБ */
        put32(dword(2), 0x6B08'EB44U);  /* 1-4-4: 0xEB, 4 холостих такти; 1-1-4: 0x6B, 8 тактів */
        put32(dword(7), 0x520F'200CU);  /* тип1 4 КБ опкодом 0x20, тип2 32 КБ опкодом 0x52 */
        put32(dword(8), 0x0000'D810U);  /* тип3 64 КБ опкодом 0xD8, тип4 не використовується */
        put32(dword(9), 0x02U | (erase_time(2, 1) << 4)     /* 4 КБ  — 48 мс */
                              | (erase_time(0, 2) << 11)    /* 32 КБ — 128 мс */
                              | (erase_time(9, 1) << 18));  /* 64 КБ — 160 мс */
        put32(dword(10), 0xFFFF'FF8CU); /* сторінка програмування 2^8 = 256 байтів */
        put32(dword(14), 0x0050'0000U); /* QER = 0b101: QE — біт 1 у SR2, читання 0x35, запис 0x31 */
    }

    void write_byte(std::uint8_t b)
    {
        if (qpi_) {
            return;  /* у QPI однолінійних команд кристал не чує взагалі */
        }
        switch (stage_) {
        case Stage::Opcode:
            switch (b) {
            case 0x9F:
                /* Понад межу зсув бітів зчитується як нулі — класична пастка
                   bring-up на максимальній частоті шини. */
                resp_ = clock_ > kIdMaxHz ? Resp::Zero : Resp::Id;
                stage_ = Stage::Data;
                break;
            case 0x05:
                resp_ = Resp::Status;
                stage_ = Stage::Data;
                break;
            case 0x5A:
                resp_ = Resp::Idle;
                stage_ = Stage::Address;
                break;
            default:
                resp_ = Resp::Idle;
                stage_ = Stage::Data;
                break;
            }
            break;
        case Stage::Address:
            addr_ = (addr_ << 8) | b;
            if (++addr_bytes_ == 3) {
                stage_ = Stage::Dummy;
            }
            break;
        case Stage::Dummy:
            cursor_ = addr_;  /* холостий такт з'їдено — далі йдуть дані */
            resp_ = Resp::Rom;
            stage_ = Stage::Data;
            break;
        case Stage::Data:
            break;
        }
    }

    std::uint8_t read_byte()
    {
        if (qpi_) {
            return 0xFF;  /* MISO лишається в неактивному стані */
        }
        switch (resp_) {
        case Resp::Id: {
            std::uint8_t v = id_index_ < kId.size() ? kId[id_index_] : std::uint8_t{0xFF};
            /* Опитування посеред циклу стирання: внутрішній контролер
               спотворює перший байт відповіді. */
            if (id_index_ == 0 && busy()) {
                v = 0xFF;
            }
            ++id_index_;
            return v;
        }
        case Resp::Status:
            return busy() ? 0x01 : 0x00;  /* біт 0 — WIP */
        case Resp::Rom: {
            const std::uint8_t v = cursor_ < rom_.size() ? rom_[cursor_] : std::uint8_t{0xFF};
            ++cursor_;
            return v;
        }
        case Resp::Zero:
            return 0x00;
        case Resp::Idle:
            break;
        }
        return 0xFF;
    }

    static constexpr std::size_t kTableOffset = 0x80;

    std::array<std::uint8_t, 256> rom_{};
    bool qpi_{true};                                /* завантажувач лишив кристал у QPI */
    unsigned clock_{kSourceHz / 2};                 /* 40 МГц після скидання периферії */
    std::chrono::milliseconds now_{0};
    Stage stage_{Stage::Opcode};
    Resp  resp_{Resp::Idle};
    std::uint32_t addr_{0};
    unsigned      addr_bytes_{0};
    std::size_t   cursor_{0};
    std::size_t   id_index_{0};
};

}  // namespace flash
