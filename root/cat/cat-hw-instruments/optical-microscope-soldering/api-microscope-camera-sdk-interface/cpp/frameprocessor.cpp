#include "CamSdkModern.hpp"
#include <vector>

class FrameProcessor {
public:
    static void OnFrameReceived(const cam::FrameBuffer& buffer) {
        if (buffer.IsComplete()) {
            // Конвертація масиву RAW8/RAW12 в об'єкт RGB24
            cam::Image rgbImage = buffer.ConvertToRGB24();

            // Запікання метрологічної сітки в буфер кадру
            rgbImage.OverlayMeasurementGrid(50 /* крок 50px */, cam::Color::Green());

            // Фіксація кадру на диску у стиснутому вигляді
            rgbImage.SaveAsJPEG("inspection_snapshot.jpg", 90);
        }
    }
};

void StartStreaming(std::shared_ptr<cam::Device>& camera) {
    // Встановлення обробника подій через лямбда-вираз
    camera->RegisterCallback([](const cam::FrameBuffer& buf) {
        FrameProcessor::OnFrameReceived(buf);
    });
    camera->StartGrabbing();
}
