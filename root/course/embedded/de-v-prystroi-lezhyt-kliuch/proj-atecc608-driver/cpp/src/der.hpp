// Пакування сирої пари (R, S) у підпис ASN.1 DER — саме такий підпис іде в
// повідомленні CertificateVerify.
#pragma once

#include <cstdint>
#include <span>
#include <vector>

#include "secure_element.hpp"

namespace atecc {

[[nodiscard]] std::vector<std::uint8_t> encodeDerSignature(
    std::span<const std::uint8_t, kSignatureSize> raw);

} // namespace atecc
