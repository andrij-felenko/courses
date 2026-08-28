#include <string>
#include <cstdint>

namespace shell {
// Концептуальне представлення змінної оболонки на C++
struct ShellVariable {
    enum Flags : uint32_t {
        None = 0,
        Exported = 1 << 0,
        ReadOnly = 1 << 1,
        Integer  = 1 << 2,
        Array    = 1 << 3
    };

    std::string name;
    std::string value;
    uint32_t attributes{None};
};
}
