void load_plugins(const fs::path& folder, ExportRegistry& registry) {
    HostImpl host(registry);
    int loaded = 0, failed = 0;

    std::vector<fs::path> files;               // зібрати кандидатів і впорядкувати
    for (const auto& entry : fs::directory_iterator(folder)) {
        const fs::path& p = entry.path();
        if (p.extension() == ".so" && p.filename().string().front() != '_')
            files.push_back(p);                // службові файли на "_" — не плагіни
    }
    std::sort(files.begin(), files.end());

    for (const auto& file : files) {
        try {
            RegisterFn reg = load_one(file);   // фази 1-2: завантажити + звірити версію

            // -- фаза «register»: знову ЧУЖИЙ код, знову під пасткою --
            // Пастка ловить лише C++-виняток з плагіна; сегфолт вона НЕ спіймає —
            // за цією межею потрібна вже пісочниця (див. периметр довіри нижче).
            try {
                reg(host);                     // плагін вписує себе в реєстр
            } catch (const std::exception& e) {
                throw PluginError(file.filename().string()
                                  + ": plugin_register кинув " + e.what());
            }
            ++loaded;
        } catch (const PluginError& e) {
            // ЄДИНЕ місце, де збій плагіна гаситься: логуємо й беремо наступний.
            warn(std::string("плагін пропущено — ") + e.what());
            ++failed;
            continue;                          // ядро НЕ падає, цикл іде далі
        }
    }
    info("плагінів завантажено: " + std::to_string(loaded)
         + ", пропущено: " + std::to_string(failed));
}
