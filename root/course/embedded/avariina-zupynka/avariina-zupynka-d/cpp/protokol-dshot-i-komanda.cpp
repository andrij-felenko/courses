// Зупинка потоку DMA та заповнення буфера командою Motor Stop
auto& stream = *reinterpret_cast<DMA_Stream_TypeDef*>(DMA2_Stream5_BASE);
stream.CR &= ~DMA_SxCR_EN;
while (stream.CR & DMA_SxCR_EN) {
    // Очікування зупинки передачі
}

std::fill(dshotDmaBuffer.begin(), dshotDmaBuffer.end(), DshotCmdMotorStopPattern);

stream.NDTR = static_cast<uint16_t>(dshotDmaBuffer.size());
stream.CR |= DMA_SxCR_EN;
