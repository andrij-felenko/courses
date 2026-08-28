#include <iostream>
#include <iomanip>

void runGroundDetectorSimulationCpp() {
    GroundDetectorParams params{};
    params.maxVzAbs = 0.15f;
    params.maxGyroAbs = 0.20f;
    params.hoverThrRatio = 0.30f;
    params.confThresholdLand = 0.85f;
    params.confThresholdDrop = 0.20f;
    params.timeRiseSec = 0.50f;
    params.timeDecaySec = 0.25f;
    params.disarmRampTimeSec = 0.40f;

    GroundDetectorModule detector{params};
    const float hoverThrust = 0.45f;
    const float dt = 0.02f; // 50 Гц

    for (int step = 0; step < 100; ++step) {
        const float timeSec = static_cast<float>(step) * dt;
        float vz{0.0f}, gyro{0.0f}, accelZ{0.0f}, thrust{0.0f};

        if (timeSec < 0.5f) {
            // Фаза 1: Спуск
            vz = -0.55f;
            gyro = 0.04f;
            accelZ = -9.81f;
            thrust = 0.40f;
        } else if (timeSec >= 0.5f && timeSec < 0.54f) {
            // Фаза 2: Удар об ґрунт
            vz = -0.05f;
            gyro = 0.08f;
            accelZ = -18.5f;
            thrust = 0.12f;
        } else if (timeSec >= 0.54f && timeSec < 0.62f) {
            // Фаза 3: Пружний відскок
            vz = +0.25f;
            gyro = 0.15f;
            accelZ = -8.5f;
            thrust = 0.10f;
        } else {
            // Фаза 4: Нерухома опора
            vz = 0.01f;
            gyro = 0.02f;
            accelZ = -9.81f;
            thrust = 0.08f;
        }

        detector.update(vz, gyro, accelZ, thrust, hoverThrust, dt);

        if (step % 10 == 0 || detector.isDisarmRequested()) {
            std::cout << std::fixed << std::setprecision(2)
                      << "T=" << timeSec << "s | State=" << static_cast<int>(detector.state())
                      << " | Conf=" << detector.confidence()
                      << " | ThrScale=" << detector.throttleScale()
                      << " | FreezeI=" << detector.areITermsFrozen()
                      << " | Disarm=" << detector.isDisarmRequested() << "\n";
        }

        if (detector.state() == GroundModuleState::Disarmed) {
            std::cout << ">>> Успішне розброєння на часі T=" << timeSec << "s <<<\n";
            break;
        }
    }
}
