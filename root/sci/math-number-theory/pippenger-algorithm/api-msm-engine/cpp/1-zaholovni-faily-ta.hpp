#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <memory>
#include <expected>
#include <string_view>
#include <vector>
#include <future>

namespace msm {

/* Коди результатів та помилок MSM */
enum class Status : int32_t {
    Success           =  0,
    NullPointer       = -1,
    InvalidSize       = -2,
    OutOfMemory       = -3,
    InvalidCurve      = -4,
    PointNotOnCurve   = -5,
    BackendFailed     = -6,
    InvalidConfig     = -7
};

/* Підтримувані криві */
enum class CurveId : uint32_t {
    BN254     = 1,
    BLS12_381 = 2,
    Secp256k1 = 3
};

/* Апаратні бекенди */
enum class Backend : uint32_t {
    CpuScalar = 0,
    CpuAvx512 = 1,
    GpuCuda   = 2
};

/* 256-бітний елемент поля */
struct FieldElement256 {
    std::array<uint64_t, 4> limbs{};

    [[nodiscard]] constexpr bool is_zero() const noexcept {
        return (limbs[0] | limbs[1] | limbs[2] | limbs[3]) == 0;
    }
};

/* Афінна точка (x, y) */
struct PointAffine {
    FieldElement256 x{};
    FieldElement256 y{};
    bool is_infinity{true};

    static constexpr PointAffine infinity() noexcept {
        return PointAffine{{}, {}, true};
    }
};

/* Проективна точка в координатах Якобі (X, Y, Z) */
struct PointJacobian {
    FieldElement256 X{};
    FieldElement256 Y{};
    FieldElement256 Z{};

    [[nodiscard]] bool is_infinity() const noexcept {
        return Z.is_zero();
    }

    static constexpr PointJacobian infinity() noexcept {
        return PointJacobian{{}, {}, {}};
    }
};

/* Конфігураційний дескриптор рушія MSM */
struct Config {
    CurveId curve{CurveId::BN254};
    Backend backend{Backend::CpuScalar};
    uint32_t window_size{0};       // 0 = автоматичний розрахунок оптимального c
    uint32_t num_threads{0};       // 0 = апаратний максимум апаратних потоків
    bool use_signed_digits{true};  // Зменшує кількість кошиків удвічі
    bool enable_radix_sort{true};  // Оптимізація локальності L3-кешу процесора
    std::span<uint8_t> arena_buffer{};
};

} // namespace msm
