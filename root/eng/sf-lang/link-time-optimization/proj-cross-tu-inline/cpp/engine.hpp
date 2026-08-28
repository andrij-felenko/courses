// engine.hpp — оголошення інтерфейсу та класів (C++)
#ifndef ENGINE_HPP
#define ENGINE_HPP

#include <cstdint>

struct IFilter {
    virtual ~IFilter() = default;
    virtual std::int32_t process(std::int32_t sample) const = 0;
};

class GainFilter final : public IFilter {
private:
    std::int32_t gain_;
public:
    explicit GainFilter(std::int32_t gain) noexcept : gain_(gain) {}
    std::int32_t process(std::int32_t sample) const noexcept override;
};

std::int32_t fast_scale(std::int32_t value, std::int32_t factor) noexcept;
std::int32_t dead_helper_function(std::int32_t x) noexcept;

#endif // ENGINE_HPP
