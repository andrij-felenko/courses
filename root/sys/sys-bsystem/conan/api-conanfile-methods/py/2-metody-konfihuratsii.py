def config_options(self):
    """Коригування доступності опцій до побудови графа."""
    # На операційній системі Windows код завжди позиційно-незалежний, прапорець fPIC не має сенсу
    if self.settings.os == "Windows":
        self.options.rm_safe("fPIC")

def configure(self):
    """Встановлення взаємозв'язків між опціями та видалення зайвих налаштувань."""
    if self.options.get_safe("shared"):
        # Для динамічних бібліотек на Linux прапорець fPIC є обов'язковим
        self.options.rm_safe("fPIC")
    
    # Якщо бібліотека є чистою реалізацією на мові C, налаштування стандартної бібліотеки C++ не потрібне
    if self.package_type == "shared-library":
        self.settings.rm_safe("compiler.libcxx")

def validate(self):
    """Перевірка сумісності конфігурації. Викликається для кожного вузла графа."""
    from conan.errors import ConanInvalidConfiguration
    from conan.tools.scm import Version

    # Заборона збірки застарілими компіляторами
    if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "11":
        raise ConanInvalidConfiguration("Цей пакет вимагає компілятор GCC 11 або новіший для підтримки концептів C++20")
    
    # Перевірка конфліктних комбінацій опцій
    if self.settings.os == "Windows" and self.options.get_safe("shared") and self.settings.compiler.get_safe("runtime") == "MT":
        raise ConanInvalidConfiguration("Динамічна бібліотека на Windows не може використовувати статичний рантайм /MT")
