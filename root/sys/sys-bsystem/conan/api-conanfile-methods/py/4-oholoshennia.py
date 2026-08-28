def requirements(self):
    """Оголошення бібліотек, які лінкуються у фінальний продукт (Host Context)."""
    # transitive_headers=True означає, що публічні заголовки цього пакета містять #include <fmt/core.h>
    self.requires("fmt/10.2.1", transitive_headers=True)
    
    # transitive_libs=True передає лінкеру вимогу лінкувати openssl усім кінцевим споживачам
    self.requires("openssl/3.2.0", transitive_headers=True, transitive_libs=True)

    if self.options.get_safe("with_compression", True):
        self.requires("zlib/1.3.1")

def build_requirements(self):
    """Оголошення інструментів, що мають виконуватися на хост-машині збірки (Build Context)."""
    # Системи збірки та компілятори
    self.tool_requires("cmake/[>=3.25]")
    self.tool_requires("ninja/1.11.1")
    
    # Генератори коду (виконуються на хості збірки)
    self.tool_requires("protobuf/3.21.12")
    
    # Фреймворки модульного тестування (не потрапляють у граф кінцевих користувачів)
    self.test_requires("gtest/1.14.0")
