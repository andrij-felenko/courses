struct ChannelOptions {
    uint32_t buffer_size{4096};
    uint32_t timeout_ms{500};
    bool enable_compression{false};
    bool enable_encryption{true};
};

// Зручна, самодокументована константна ініціалізація агрегату:
inline constinit ChannelOptions g_primary_channel{
    .buffer_size = 8192,
    .timeout_ms = 1000,
    .enable_compression = true
};
