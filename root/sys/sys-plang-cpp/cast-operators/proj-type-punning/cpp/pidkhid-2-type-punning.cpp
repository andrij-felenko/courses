#include <cstdint>

// У C++ [class.union] активним є лише ОДНЕ поле union.
// Читання неактивного поля є невизначеною поведінкою (UB)!
union FloatPun {
    float f;
    uint32_t u;
};

bool is_negative_union(float f) noexcept {
    FloatPun pun{.f = f};
    return (pun.u & 0x80000000u) != 0; // UB в чистому стандарті C++
}
