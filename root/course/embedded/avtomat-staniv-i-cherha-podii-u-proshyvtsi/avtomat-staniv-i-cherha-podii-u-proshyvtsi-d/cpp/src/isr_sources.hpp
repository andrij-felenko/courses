#pragma once

#include <cstdint>

/*
 * Точки входу переривань. Прив'яжіть кожну до відповідного вектора свого
 * мікроконтролера (SysTick, EXTI, USART, COMP). Зв'язування зовнішнє, "C",
 * бо таблиця векторів заповнюється з асемблерного startup-файла й спотворені
 * імена C++ їй нічого не скажуть.
 *
 * Усі вони дотримуються однієї дисципліни: прочитати апаратний регістр,
 * скласти подію, покласти її в чергу й вийти. Жодних переходів автомата,
 * жодних звернень до дисплея, жодних циклів очікування.
 */
extern "C" {

void evse_isr_systick_1ms();
void evse_isr_emergency_button();
void evse_isr_reset_button();
void evse_isr_overcurrent(std::uint16_t amperes);
void evse_isr_leakage(std::uint16_t milliamps);
void evse_isr_rfid_rx(std::uint8_t byte);

} // extern "C"
