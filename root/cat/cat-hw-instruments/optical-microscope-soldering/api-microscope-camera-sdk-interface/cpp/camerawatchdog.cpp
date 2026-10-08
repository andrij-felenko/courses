#include "CamSdkModern.hpp"
#include <thread>
#include <chrono>
#include <iostream>

class CameraWatchdog {
public:
    static void MonitorAndRecover(std::shared_ptr<cam::Device>& camera) {
        std::thread watchdogThread([&camera]() {
            while (true) {
                std::this_thread::sleep_for(std::chrono::seconds(1));
                if (camera && !camera->IsConnected()) {
                    std::cerr << "Увага: Камера відключена. Спроба відновлення..." << std::endl;
                    camera->Close();
                    
                    while (true) {
                        try {
                            auto devices = cam::System::GetInstance().EnumerateDevices();
                            if (!devices.empty()) {
                                camera = cam::System::GetInstance().CreateDevice(devices[0]);
                                camera->Open();
                                camera->SetExposureTime(2500.0);
                                camera->StartGrabbing();
                                std::cout << "Автоматичне відновлення успішне!" << std::endl;
                                break;
                            }
                        } catch (...) {
                            // Очікування наступного циклу опитування
                        }
                        std::this_thread::sleep_for(std::chrono::seconds(2));
                    }
                }
            }
        });
        watchdogThread.detach();
    }
};
