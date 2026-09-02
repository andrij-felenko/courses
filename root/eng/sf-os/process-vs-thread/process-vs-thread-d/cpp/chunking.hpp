#pragma once

#include <cstddef>
#include <span>
#include <stdexcept>
#include <vector>

// Ділить діапазон на parts майже рівних часток. Кожна частка — span:
// сам масив не копіюється, усі робітники дивляться в ту саму пам'ять.
inline std::vector<std::span<const int>> splitEvenly(std::span<const int> all,
                                                     std::size_t parts)
{
    if (parts == 0)
        throw std::invalid_argument("потрібен щонайменше один робітник");

    std::vector<std::span<const int>> pieces;
    pieces.reserve(parts);

    const std::size_t base = all.size() / parts;
    const std::size_t rest = all.size() % parts;
    std::size_t pos = 0;

    for (std::size_t i = 0; i < parts; ++i) {
        const std::size_t len = base + (i < rest ? 1 : 0);
        pieces.push_back(all.subspan(pos, len));
        pos += len;
    }
    return pieces;
}
