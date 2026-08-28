void startSecureCommissioning(otInstance *instance, std::string_view pskd)
{
    auto callback = [](otError error, void *ctx) {
        if (error == OT_ERROR_NONE) {
            std::cout << "[Joiner] Комісіонування успішне! Запуск Thread..." << std::endl;
            otThreadSetEnabled(static_cast<otInstance*>(ctx), true);
        } else {
            std::cerr << "[Joiner Помилка] Код: " << error << std::endl;
        }
    };

    otJoinerStart(instance, pskd.data(), nullptr, "VendorLab", "TempSensor", "v1.0", nullptr,
                  callback, instance);
}
