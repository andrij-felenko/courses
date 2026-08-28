#pragma once
#include "RingBuffer.hpp"
#include <cstdint>
#include <string>

// Оголошення зручних псевдонімів
using RawByteBuffer = RingBuffer<std::uint8_t, 256>;
using SignalBuffer  = RingBuffer<double, 64>;
using LogQueue      = RingBuffer<std::string, 16>;

// Заборона генерації коду в одиницях трансляції, що включають цей заголовок
extern template class RingBuffer<std::uint8_t, 256>;
extern template class RingBuffer<double, 64>;
extern template class RingBuffer<std::string, 16>;
