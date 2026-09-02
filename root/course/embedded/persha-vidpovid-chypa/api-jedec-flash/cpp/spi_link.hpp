#pragma once

#include <chrono>
#include <cstdint>
#include <span>

namespace flash {

/* Контракт шини, якого драйверу ідентифікації досить. Під ним може стояти
   периферія мікроконтролера або симулятор кристала з цієї теки. */
class SpiLink {
public:
    virtual ~SpiLink() = default;

    /* Ставить частоту й повертає ту, що реально вийшла після цілочисельного дільника. */
    virtual unsigned set_clock(unsigned hz) = 0;
    [[nodiscard]] virtual unsigned clock() const noexcept = 0;

    /* Лічильник часу для тайм-аутів очікування. */
    [[nodiscard]] virtual std::chrono::milliseconds now() = 0;

    /* Повний дуплекс: порожній tx — женемо нулі, порожній rx — відповідь відкидаємо. */
    virtual void transfer(std::span<const std::uint8_t> tx, std::span<std::uint8_t> rx) = 0;

    /* Передача по чотирьох лініях: потрібна рівно для виходу з режиму QPI. */
    virtual void quad_write(std::span<const std::uint8_t> tx) = 0;

protected:
    friend class ChipSelect;
    virtual void select() = 0;
    virtual void release() noexcept = 0;
};

/* Межі транзакції як час життя об'єкта: CS підніметься і на ранньому return,
   і на винятку посеред обміну. */
class ChipSelect {
public:
    explicit ChipSelect(SpiLink &link) : link_{link} { link_.select(); }
    ~ChipSelect() { link_.release(); }

    ChipSelect(const ChipSelect &) = delete;
    ChipSelect &operator=(const ChipSelect &) = delete;

private:
    SpiLink &link_;
};

/* Те саме для частоти: на час опитування знижуємо, на виході повертаємо як було. */
class ClockGuard {
public:
    ClockGuard(SpiLink &link, unsigned hz) : link_{link}, saved_{link.clock()}
    {
        link_.set_clock(hz);
    }
    ~ClockGuard() { link_.set_clock(saved_); }

    ClockGuard(const ClockGuard &) = delete;
    ClockGuard &operator=(const ClockGuard &) = delete;

private:
    SpiLink &link_;
    unsigned saved_;
};

/* Одна транзакція: командні байти по MOSI, потім читання відповіді з MISO.
   Розривати CS усередині не можна — чип забуде опкод. */
inline void command(SpiLink &link,
                    std::span<const std::uint8_t> cmd,
                    std::span<std::uint8_t> rsp)
{
    ChipSelect cs{link};
    if (!cmd.empty()) {
        link.transfer(cmd, {});
    }
    if (!rsp.empty()) {
        link.transfer({}, rsp);
    }
}

}  // namespace flash
