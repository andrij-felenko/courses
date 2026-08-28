def package_info(self):
    """Оголошення експортованих бібліотек, прапорців та CMake-цілей."""
    self.cpp_info.libs = ["network_core", "network_crypto"]
    self.cpp_info.includedirs = ["include"]
    self.cpp_info.libdirs = ["lib"]
    self.cpp_info.defines = ["NETWORK_ENGINE_STATIC=1"]
    
    # Канонічне ім'я файлу конфігурації: find_package(NetworkEngine CONFIG REQUIRED)
    self.cpp_info.set_property("cmake_file_name", "NetworkEngine")
    
    # Канонічне ім'я імпортованої цілі: NetworkEngine::NetworkEngine
    self.cpp_info.set_property("cmake_target_name", "NetworkEngine::NetworkEngine")

    # Системні бібліотеки цільової операційної системи
    if self.settings.os in ["Linux", "FreeBSD"]:
        self.cpp_info.system_libs = ["pthread", "dl", "rt", "m"]
    elif self.settings.os == "Windows":
        self.cpp_info.system_libs = ["ws2_32", "crypt32", "secur32"]
    elif self.settings.os == "Macos":
        self.cpp_info.frameworks = ["CoreFoundation", "Security"]
