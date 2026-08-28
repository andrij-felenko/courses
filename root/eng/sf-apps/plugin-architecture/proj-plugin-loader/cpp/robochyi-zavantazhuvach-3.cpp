int main() {
    ExportRegistry registry;
    load_plugins("plugins", registry);   // тека могла мати й гнилі .so

    // ядро працює з тими, що завантажились; несправні просто відсутні в реєстрі
    Document doc = /* якийсь документ ядра */ {};
    if (registry.has("md")) {
        std::vector<std::uint8_t> data = registry.exportAs("md", doc);
        (void)data;   // ... ядро віддає байти користувачеві
    }
    return 0;
}
