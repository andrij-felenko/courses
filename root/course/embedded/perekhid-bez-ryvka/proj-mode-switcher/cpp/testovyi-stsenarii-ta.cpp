int main() {
    FlightManager mgr;
    constexpr float dt = 0.02f;
    float alt = 42.0f;
    float stick = 0.56f;

    std::cout << "Час[с] | Режим | Висота[м] | Вихід[%] | Стрибок dU\n";
    std::cout << "--------------------------------------------------\n";

    float prev_out = 0.56f;

    for (int step = 0; step <= 750; ++step) {
        const float t = static_cast<float>(step) * dt;

        if (step == 250) {
            mgr.switch_mode(FlightMode::AltHold, alt, alt);
            std::cout << ">>> [t=5.0s] ПЕРЕМИКАННЯ: MANUAL -> ALT_HOLD <<<\n";
        }

        if (step == 500) {
            mgr.switch_mode(FlightMode::AutoMission, alt, 80.0f);
            std::cout << ">>> [t=10.0s] ПЕРЕМИКАННЯ: ALT_HOLD -> AUTO_MISSION (Target=80m) <<<\n";
        }

        const float out = mgr.step(stick, alt, dt);
        const float du = std::abs(out - prev_out);

        if (step == 249 || step == 250 || step == 251 ||
            step == 499 || step == 500 || step == 501) {
            std::cout << t << "s | Mode: " << static_cast<int>(mgr.current_mode())
                      << " | Alt: " << alt << " | Out: " << out << " | dU: " << du << "\n";
        }

        alt += (out - 0.56f) * 10.0f * dt;
        prev_out = out;
    }

    return 0;
}
