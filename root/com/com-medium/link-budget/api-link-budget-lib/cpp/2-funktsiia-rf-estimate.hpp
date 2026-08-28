// Алгоритм обчислення необхідної потужності P_TX (C++23)
namespace rf {
[[nodiscard]] inline std::expected<float, Status>
estimate_required_tx_power(float target_margin_db,
                           const ChannelParams& channel,
                           const RxParams& rx,
                           float tx_gain_dbi,
                           float tx_cable_loss_db) noexcept {
    if (channel.frequency_mhz <= 0.0f) return std::unexpected(Status::FreqOutOfRange);
    if (channel.distance_km <= 0.0f)  return std::unexpected(Status::ZeroDistance);

    const float path_loss = channel.total_path_loss();
    const float sensitivity = rx.sensitivity();
    const float target_p_rx = sensitivity + target_margin_db;

    return target_p_rx + path_loss - tx_gain_dbi + tx_cable_loss_db - 
           rx.rx_antenna_gain_dbi + rx.rx_cable_loss_db;
}
} // namespace rf
