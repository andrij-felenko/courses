#pragma once

#include <expected>

#include "firmware_descriptor.hpp"

namespace fw {

/* Повна перевірка релізу перед передачею керування. Тіло образу верифікатор
   дістає сам — інакше довелося б спершу довіритись полю payload_size,
   тобто взяти на віру ще не перевірений дескриптор. */
[[nodiscard]] std::expected<void, VerifyError> verify_release(const Descriptor& descriptor) noexcept;

}  // namespace fw
