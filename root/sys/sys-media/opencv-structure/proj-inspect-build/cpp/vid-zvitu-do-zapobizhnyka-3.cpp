int main(int argc, char** argv)
{
    const std::string mode = argc > 1 ? argv[1] : "--report";

    if (mode == "--debug")   // чому саме плагін не завантажився
        cv::utils::logging::setLogLevel(cv::utils::logging::LOG_LEVEL_DEBUG);

    if (mode != "--check") {
        reportVersion();
        std::cout << "Модулі: "
                  << buildInfoField("OpenCV modules", "To be built") << "\n"
                  << "Contrib: "
                  << buildInfoField("Extra modules", "Version control (extra)")
                  << "\n";
        reportBackends("Файли й потоки", reg::getStreamBackends(),
                                         reg::getStreamBackendPluginVersion);
        reportBackends("Камери",         reg::getCameraBackends(),
                                         reg::getCameraBackendPluginVersion);
        reportBackends("Запис",          reg::getWriterBackends(),
                                         reg::getWriterBackendPluginVersion);
        reportCompute();
        std::cout << "\n";
    }

    const AppConfig cfg{};               // насправді — з конфігурації застосунку
    return verify(requirementsOf(cfg)) ? 0 : 1;
}
