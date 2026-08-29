// report.hpp — друк бюджету. Рахує pipeline.hpp, форматує report.cpp.
//
// Розділення не косметичне: на бортовій діагностиці той самий Summary піде
// в телеметрію, а не в термінал, і рахунок туди їде без жодного потоку виводу.
#pragma once

#include <span>
#include <string_view>

#include "latency/pipeline.hpp"

namespace latency::report {

// Повна таблиця ланок тракту з підсумком і поділом на електроніку й фізику.
void print_track(const Track& track);

// Що затримка робить із контуром: фазовий зсув на частоті маневрування
// control_hz і сліпий шлях на швидкості speed_mps.
void print_dynamics(std::string_view label, const Summary& budget,
                    double control_hz, double speed_mps);

// Один рядок на тракт: typ, max, джитер, найтовща ланка.
void print_comparison(std::string_view heading, std::span<const Track> tracks);

}  // namespace latency::report
