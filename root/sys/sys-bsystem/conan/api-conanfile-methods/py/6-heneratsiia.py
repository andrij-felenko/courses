def generate(self):
    """Створення файлів CMakeToolchain, CMakeDeps та змінних середовища."""
    from conan.tools.cmake import CMakeToolchain, CMakeDeps
    from conan.tools.env import VirtualBuildEnv, VirtualRunEnv

    # Створення conan_toolchain.cmake із точними прапорцями компілятора
    tc = CMakeToolchain(self)
    tc.variables["BUILD_TESTS"] = False
    tc.variables["ENABLE_CUSTOM_ALLOCATOR"] = True
    tc.generate()

    # Створення <Pkg>Config.cmake файлів для всіх знайдених requirements
    deps = CMakeDeps(self)
    deps.generate()

    # Експорт змінних середовища для запуску інструментів з tool_requires (наприклад, protoc)
    build_env = VirtualBuildEnv(self)
    build_env.generate()
