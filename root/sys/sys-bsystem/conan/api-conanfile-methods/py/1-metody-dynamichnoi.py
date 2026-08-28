def set_name(self):
    """Динамічне визначення імені пакета перед побудовою графа."""
    self.name = "distributed_telemetry"

def set_version(self):
    """Динамічне зчитування версії з файлу версії або системних змінних."""
    from conan.tools.files import load
    import os
    version_file = os.path.join(self.recipe_folder, "version.txt")
    if os.path.exists(version_file):
        self.version = load(self, version_file).strip()
    else:
        self.version = "0.1.0-dev"
