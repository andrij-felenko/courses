type MessagePayloadSpectralStatus struct {
    TimeBootMs         uint32  `mavlink:"0"`
    IntegrationTimeMs  float32 `mavlink:"4"`
    SensorTemperature  float32 `mavlink:"8"`
    SpectralIrradiance uint16  `mavlink:"12"`
    FilterMode         uint8   `mavlink:"14"`
    StatusFlags        uint8   `mavlink:"15"`
    CalibrationCrc     uint32  `mavlink:"16,extension"`
    GainLevel          uint8   `mavlink:"20,extension"`
}

func (m *MessagePayloadSpectralStatus) GetID() uint32 {
    return 42010
}
