/* Формування рядка прив'язки до каналу для поля c= */
[[nodiscard]] std::string build_channel_binding_field(std::span<const uint8_t> cert_der) {
    byte_block cert_hash = scram_service::compute_sha256(cert_der);

    constexpr std::string_view prefix = "p=tls-server-end-point,,";
    std::vector<uint8_t> raw_binding(prefix.begin(), prefix.end());
    raw_binding.insert(raw_binding.end(), cert_hash.begin(), cert_hash.end());

    return base64_encode(raw_binding);
}
