def package_info(self):
    self.cpp_info.set_property("cmake_file_name", "OpenSSL")

    # Компонент криптографії
    self.cpp_info.components["crypto"].libs = ["crypto"]
    self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
    if self.settings.os in ["Linux", "FreeBSD"]:
        self.cpp_info.components["crypto"].system_libs = ["dl", "pthread"]

    # Компонент SSL, що залежить від внутрішнього компонента crypto
    self.cpp_info.components["ssl"].libs = ["ssl"]
    self.cpp_info.components["ssl"].requires = ["crypto"]
    self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
