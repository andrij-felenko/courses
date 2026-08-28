#include <chrono>
#include <iostream>

using namespace std::chrono;

// Зручні літерали дат
auto date = 2026y / August / 19d;
bool valid = date.ok();

// Арифметика дат
auto next_month = date + months(1);

// Робота з часовими поясами
zoned_time kyiv_time{"Europe/Kyiv", system_clock::now()};
