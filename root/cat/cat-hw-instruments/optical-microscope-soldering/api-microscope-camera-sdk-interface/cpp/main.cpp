#include <iostream>
#include <vector>
#include <memory>
#include "CamSdkModern.hpp"

int main() {
    try {
        // Ініціалізація екземпляра підсистеми керування
        auto& system = cam::System::GetInstance();
        system.Initialize();

        // Пошук та перелік пристроїв на шині USB 3.0 / GigE
        std::vector<cam::DeviceInfo> devices = system.EnumerateDevices();
        if (devices.empty()) {
            std::cerr << "Не знайдено жодної камери для контролю." << std::endl;
            system.Shutdown();
            return -1;
        }

        // Використання RAII-обгортки для пристрою
        auto camera = system.CreateDevice(devices[0]);
        camera->Open();
        std::cout << "Підключено до камери: " << camera->GetModelName() << std::endl;

        // Конфігурування системного буферизованого каналу
        camera->SetPacketSize(9000);

        // Автоматичне закриття камери та звільнення ресурсів при виході з області видимості
        camera->Close();
        system.Shutdown();
    } catch (const cam::CameraException& ex) {
        std::cerr << "Критична помилка SDK: " << ex.what() << std::endl;
        return -1;
    }
    return 0;
}
