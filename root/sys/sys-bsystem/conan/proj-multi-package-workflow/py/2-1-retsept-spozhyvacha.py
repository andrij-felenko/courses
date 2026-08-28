from conan import ConanFile
from conan.tools.cmake import cmake_layout

class DaemonConan(ConanFile):
    name = "telemetry_daemon"
    version = "0.1.0"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("telemetry/1.0.0")
        self.requires("fmt/10.2.1")
        self.requires("nlohmann_json/3.11.3")

    def layout(self):
        cmake_layout(self)
