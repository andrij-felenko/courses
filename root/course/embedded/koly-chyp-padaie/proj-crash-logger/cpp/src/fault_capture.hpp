// Перехоплення фатальних винятків: асемблерний місток плюс аналітична частина.
#pragma once

namespace crash {

// Вмикає окремі вектори MemManage/BusFault/UsageFault і пастки на ділення на
// нуль та невирівняний доступ. Без цього все зводиться до одного HardFault,
// і CFSR доводиться читати вже після ескалації.
void arm() noexcept;

} // namespace crash

// Символи з таблиці векторів. Мостики оголошені extern "C": на них посилається
// і стартовий файл, і асемблерна інструкція переходу всередині самого містка.
extern "C" {
void HardFault_Handler();
void MemManage_Handler();
void BusFault_Handler();
void UsageFault_Handler();
}
