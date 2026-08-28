using PluginVersionFn = std::string (*)(cv::VideoCaptureAPIs, int&, int&);

// hasBackend() для плагіна — це справжня спроба завантажити файл.
static bool loads(cv::VideoCaptureAPIs api)
{
    try { return reg::hasBackend(api); }
    catch (const cv::Exception&) { return false; }
}

// Питати версію плагіна МОЖНА лише в плагіна: для вбудованого бекенда
// всередині спрацьовує CV_Assert і летить cv::Exception.
// Повертається опис із заголовка плагіна, а не шлях до файлу.
static std::string pluginNote(PluginVersionFn version, cv::VideoCaptureAPIs api)
{
    int abi = 0, apiVer = 0;
    try {
        const std::string desc = version(api, abi, apiVer);
        return " ← " + desc + " (ABI " + std::to_string(abi)
             + ", API " + std::to_string(apiVer) + ")";
    } catch (const cv::Exception&) {
        return " ← файл плагіна не відкрито";
    }
}

static void reportBackends(const char* what,
                           const std::vector<cv::VideoCaptureAPIs>& list,
                           PluginVersionFn version)
{
    std::cout << what << " (" << list.size() << ")\n";
    for (cv::VideoCaptureAPIs api : list) {
        const bool builtIn = reg::isBackendBuiltIn(api);
        const bool alive   = loads(api);
        std::cout << (alive ? "  + " : "  - ")
                  << reg::getBackendName(api)
                  << (builtIn ? "  вбудований" : "  плагін");
        if (!builtIn) std::cout << pluginNote(version, api);
        std::cout << "\n";
    }
}
