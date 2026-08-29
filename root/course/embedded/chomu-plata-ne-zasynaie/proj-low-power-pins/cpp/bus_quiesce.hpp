// Зупинка послідовних інтерфейсів перед сном.
//
// Одне питання на весь модуль: чи можна вже гасити тактування й живлення, не
// обірвавши кадр і не лишивши шину заклиненою. Перевантаження, а не три різні
// імена: для викликача це одна й та сама дія над різним залізом.
#pragma once

#include <chrono>

#include "mcu.hpp"
#include "status.hpp"

namespace lowpower {

// Чекає TC (передача завершена), а не TXE (буфер вільний), і аж тоді знімає UE.
[[nodiscard]] Status quiesce(mcu::UsartBlock& u, std::chrono::microseconds timeout);

// Чекає спустошення черги передачі FTLVL і зняття BSY, тоді знімає SPE.
[[nodiscard]] Status quiesce(mcu::SpiBlock& s, std::chrono::microseconds timeout);

// Чекає зняття BUSY, тоді знімає PE — це відпускає SDA і SCL у високий імпеданс.
[[nodiscard]] Status quiesce(mcu::I2cBlock& i, std::chrono::microseconds timeout);

// Усі три шини плати; повертає першу ж відмову.
[[nodiscard]] Status quiesce_all(std::chrono::microseconds timeout);

// Дев'ять тактів SCL руками плюс умова STOP — коли веденого знеструмили
// посеред байта і він лишився тримати лінію.
[[nodiscard]] Status recover_i2c_bus();

} // namespace lowpower
