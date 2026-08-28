if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    registry = ExportRegistry()
    load_plugins(Path("plugins"), registry)       # тека могла мати й гнилі файли

    # ядро працює з тими, що завантажились; несправні просто відсутні в реєстрі
    doc = ...                                      # якийсь документ ядра
    if "md" in registry._by_ext:
        data = registry.export_as("md", doc)
