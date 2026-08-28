// main_cpp20.cpp — Тестування C++20 заголовка
#include "device_cpp20.hpp"

void usart_init_cpp20() {
    using namespace micro32::hal::usart1;

    // Типобезпечне увімкнення та вибір довжини слова через enum class
    CR1::set_field<CR1_Fields::M>(CR1_Fields::M_Enum::M_8Bit);
    CR1::set_field<CR1_Fields::UE>(true);

    // Опитування прапорця готовності передавача
    while (!SR_Fields::TXE::decode(SR::read())) {
        // Очікування
    }

    // Безпечний запис даних
    DR::write(0x55U);
}

int main() {
    usart_init_cpp20();
    return 0;
}
