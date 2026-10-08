#include "CamSdkModern.hpp"
#include <cmath>
#include <vector>

void ConfigureSensorPipeline(std::shared_ptr<cam::Device>& camera) {
    // Регулювання витримки експозиції та підсилення
    camera->SetExposureTime(2500.0); // 2500 мкс
    camera->SetGain(6.0);            // 6 дБ

    // Визначення геометрії кадру ROI
    cam::Rect roi{128, 128, 1024, 768};
    camera->SetROI(roi);

    // Увімкнення режиму Binning 2x2
    camera->SetBinning(cam::BinningMode::Sum2x2);

    // Заповнення та застосування кастомної таблиці LUT для виявлення дефектів
    std::vector<uint16_t> lut(4096);
    for (size_t i = 0; i < lut.size(); ++i) {
        double normalized = static_cast<double>(i) / 4095.0;
        lut[i] = static_cast<uint16_t>(std::pow(normalized, 0.8) * 4095.0);
    }
    camera->UploadLUT(lut);
}
