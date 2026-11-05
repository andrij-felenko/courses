#pragma once

#include <chrono>
#include <thread>

/**
 * @file LvcBuffer.hpp
 * @brief Оголошення класу LvcBuffer для керування тристабільним буфером 74LVC1G125 (активний рівень /OE — LOW).
 */
class LvcBuffer {
public:
    /**
     * @brief Конструктор драйвера буфера.
     * @param oe_pin Номер апаратного пін-у /OE (Output Enable).
     */
    explicit LvcBuffer(int oe_pin);

    /**
     * @brief Деструктор (RAII): гарантовано переводить вихід у стан високого імпедансу (Hi-Z, вимкнено).
     */
    ~LvcBuffer();

    // Заборона копіювання для запобігання дублюванню керування одним апаратним піном
    LvcBuffer(const LvcBuffer&) = delete;
    LvcBuffer& operator=(const LvcBuffer&) = delete;

    // Дозволяємо перенесення
    LvcBuffer(LvcBuffer&& other) noexcept;
    LvcBuffer& operator=(LvcBuffer&& other) noexcept;

    /**
     * @brief Активує вихід буфера (подає LOW на пін /OE).
     */
    void enable();

    /**
     * @brief Деактивує вихід буфера, пересилаючи його у стан Hi-Z (подає HIGH на пін /OE).
     */
    void disable();

    /**
     * @brief Перевіряє, чи активний вихід буфера.
     * @return true, якщо вихід увімкнено (очікується LOW на /OE), і false в іншому випадку.
     */
    [[nodiscard]] bool is_enabled() const noexcept;

    /**
     * @brief Виконує безпечне перемикання з break-before-make паузою для запобігання шинним конфліктам.
     * @param to_enable Об'єкт буфера, який треба увімкнути після вимкнення поточного.
     * @param delay Тривалість паузи захисного інтервалу.
     */
    void switch_to(LvcBuffer& to_enable, std::chrono::microseconds delay = std::chrono::microseconds(1));

private:
    int oe_pin_;
    bool enabled_;

    // Низькорівнева абстракція апаратного керування піном
    void write_pin(bool high);
};
