from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
import os

class TelemetryConan(ConanFile):
    name = "telemetry"
    version = "1.0.0"
    license = "MIT"
    author = "Embedded Team <embedded@company.internal>"
    description = "Телеметрична серіалізація та кадрування датчиків"
    topics = ("telemetry", "sensors", "serialization")
    package_type = "library"

    # Матриця комбінаторних параметрів
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        # На платформі Windows прапорець fPIC не має сенсу
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        # Для shared-бібліотек на Linux fPIC завжди активний
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        # Автоматичне налаштування шляхів збірки під генератори CMake
        cmake_layout(self)

    def generate(self):
        # Генерація файлів conan_toolchain.cmake та конфігурацій залежностей
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        # Виклик CMake у підкаталозі build
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Інсталяція артефактів у package_folder
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        # Оголошення публічних імпортованих цілей для споживачів
        self.cpp_info.libs = ["telemetry"]
        self.cpp_info.set_property("cmake_file_name", "telemetry")
        self.cpp_info.set_property("cmake_target_name", "telemetry::telemetry")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
