def source(self):
    """Отримання офіційного архіву вихідних текстів або клонування репозиторію."""
    from conan.tools.files import get, patch
    
    get(self,
        url=f"https://github.com/example/libnetwork/archive/v{self.version}.tar.gz",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        strip_root=True)
    
    # Застосування виправлень за потреби
    if os.path.exists("patches/fix-arm-build.patch"):
        patch(self, patch_file="patches/fix-arm-build.patch")
