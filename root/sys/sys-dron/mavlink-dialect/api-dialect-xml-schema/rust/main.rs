#[derive(Clone, Debug, PartialEq)]
pub struct PayloadSpectralStatusData {
    pub time_boot_ms: u32,
    pub integration_time_ms: f32,
    pub sensor_temperature: f32,
    pub spectral_irradiance: u16,
    pub filter_mode: u8,
    pub status_flags: u8,
    pub calibration_crc: u32,
    pub gain_level: u8,
}

#[derive(Clone, Debug, PartialEq)]
pub enum MavMessage {
    Heartbeat(HeartbeatData),
    PayloadSpectralStatus(PayloadSpectralStatusData),
    // Решта повідомлень діалекту...
}
