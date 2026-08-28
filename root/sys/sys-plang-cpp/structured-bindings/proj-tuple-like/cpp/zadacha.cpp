#include <cstdint>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>

namespace hw {

class Sample {
public:
    Sample(std::uint16_t code, std::string tag)
        : code_(code), tag_(std::move(tag)) {}

    double voltage() const { return code_ * (3.3 / 65535.0); }

private:
    std::uint16_t code_;
    std::string   tag_;
};

}  // namespace hw
