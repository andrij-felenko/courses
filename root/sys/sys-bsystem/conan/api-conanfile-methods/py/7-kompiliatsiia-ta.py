def build(self):
    """Конфігурація та компіляція бібліотеки через виклики системи збірки."""
    from conan.tools.cmake import CMake
    cmake = CMake(self)
    cmake.configure()
    cmake.build()

def package(self):
    """Копіювання зібраних заголовків, бібліотек та ліцензій у package_folder."""
    from conan.tools.cmake import CMake
    from conan.tools.files import copy
    import os

    cmake = CMake(self)
    cmake.install()
    
    # Обов'язкове ліцензійне очищення: збереження юридичних умов ліцензії в пакеті
    copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
