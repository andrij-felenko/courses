// iso9613_api.hpp — C++20 Обгортка бібліотеки ISO 9613-1
#ifndef ISO9613_API_HPP
#define ISO9613_API_HPP

#include "iso9613_api.h"
#include <expected>
#include <span>
#include <vector>

namespace iso9613 {

using Atmosphere = iso9613_atmosphere_t;
using Result = iso9613_result_t;
using Error = iso9613_error_t;

class Calculator {
public:
    // Обчислення для одного значення частоти
    [[nodiscard]] static std::expected<Result, Error> 
    calculate(double frequency_hz, const Atmosphere& env) noexcept {
        Result res{};
        Error err = iso9613_calculate_single(frequency_hz, &env, &res);
        if (err == ISO9613_SUCCESS) {
            return res;
        }
        return std::unexpected(err);
    }

    // Пакетне обчислення для спектральних смуг
    static Error calculate_batch(
        std::span<const double> freqs,
        std::span<double> out_db_km,
        const Atmosphere& env
    ) noexcept {
        return iso9613_calculate_spectrum(
            freqs.data(), 
            out_db_km.data(), 
            std::min(freqs.size(), out_db_km.size()), 
            &env
        );
    }
};

} // namespace iso9613

#endif /* ISO9613_API_HPP */
