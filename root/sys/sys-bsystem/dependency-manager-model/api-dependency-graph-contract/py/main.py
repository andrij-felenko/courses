from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy

class TelemetryEngineConan(ConanFile):
    name = "network-telemetry-engine"
    version = "2.4.1"
    package_type = "application"

    # Параметри конфігурації двійкового середовища
    settings = "os", "arch", "compiler", "build_type"
    
    # Користувацькі опції та значення за замовчуванням
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True
    }

    def config_options(self):
        # На платформі Windows позиційно-незалежний код не має сенсу
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        # Стандартизована структура каталогів для збірки CMake
        cmake_layout(self)

    def requirements(self):
        # Оголошення прямих бібліотечних залежностей
        self.requires("fmt/10.1.1")
        if self.options.with_ssl:
            self.requires("openssl/3.1.4", transitive_headers=True)

    def build_requirements(self):
        # Інструменти, необхідні виключно на етапі збірки на машині-хості
        self.tool_requires("cmake/3.28.1")
        self.tool_requires("ninja/1.11.1")

    def generate(self):
        # Генерація файлів інтеграції для системи збірки
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
