// Обробник фатальних винятків: асемблерний місток плюс аналітична частина на C.
#ifndef FAULT_HANDLER_H
#define FAULT_HANDLER_H

// Вмикає окремі винятки MemManage/BusFault/UsageFault і пастки на ділення на
// нуль та невирівняний доступ. Без цього все звалюється в один HardFault, і
// CFSR доводиться читати вже після ескалації.
void fault_handler_init(void);

// Символи з таблиці векторів; визначені в fault_handler.c як naked-функції.
void HardFault_Handler(void);
void MemManage_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);

#endif // FAULT_HANDLER_H
