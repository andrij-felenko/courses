from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
import os

class NetworkEngineConan(ConanFile):
    name = "network_engine"
    version = "2.4.1"
    package_type = "library"
    license = "Apache-2.0"
    author = "Infra Team <infra@company.internal>"
    url = "https://github.com/company/network_engine"
    description = "Асинхронний мережевий рушій на базі epoll/kqueue/IOCP"
    topics = ("networking", "async", "sockets")

    # Комбінаторна матриця бінарної сумісності
    settings = "os", "arch", "compiler", "build_type"
    
    # Опції збірки конкретного пакета
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": True,
    }

    def config_options(self):
        """Коригування опцій залежно від операційної системи до розрахунку графа."""
        if self.settings.os == "Windows":
            # На платформі Windows весь код позиційно-незалежний, прапорець fPIC відсутній
            self.options.rm_safe("fPIC")

    def configure(self):
        """Коригування взаємозв'язків між опціями."""
        if self.options.shared:
            # Для динамічних бібліотек на POSIX прапорець fPIC обов'язковий
            self.options.rm_safe("fPIC")

    def validate(self):
        """Перевірка обмежень платформи та версій інструментів."""
        if self.settings.compiler.get_safe("cppstd"):
            if int(str(self.settings.compiler.cppstd)) < 20:
                raise ConanInvalidConfiguration("network_engine вимагає підтримки стандарту C++20 або новішого")

    def layout(self):
        """Декларація стандартної структури каталогів."""
        cmake_layout(self)

    def requirements(self):
        """Оголошення бібліотечних залежностей цільової платформи."""
        self.requires("fmt/10.2.1", transitive_headers=True)
        if self.options.with_ssl:
            self.requires("openssl/3.2.0", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        """Оголошення інструментів середовища збірки та генераторів коду."""
        self.tool_requires("cmake/[>=3.25]")
        self.tool_requires("ninja/1.11.1")

    def source(self):
        """Завантаження вихідного коду (виконується один раз для рецепта)."""
        get(self, 
            url=f"https://github.com/company/network_engine/archive/v{self.version}.tar.gz",
            sha256="7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b",
            strip_root=True)

    def generate(self):
        """Генерація інтеграційних файлів для системи збірки (CMakeToolchain/CMakeDeps)."""
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SSL_SUPPORT"] = self.options.with_ssl
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        """Виклик процесу конфігурації та компіляції."""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        """Копіювання зібраних бінарників та заголовків у каталог package_folder."""
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        """Опис контракту бібліотеки для генераторів споживачів."""
        self.cpp_info.libs = ["network_engine"]
        self.cpp_info.set_property("cmake_file_name", "network_engine")
        self.cpp_info.set_property("cmake_target_name", "network_engine::network_engine")
        
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32"]
