# Активація покомпонентного режиму для RPM
set(CPACK_RPM_COMPONENT_INSTALL ON)

# Обов'язкові поля для RPM
set(CPACK_RPM_PACKAGE_LICENSE "Apache-2.0")
set(CPACK_RPM_PACKAGE_GROUP "Applications/System")
set(CPACK_RPM_PACKAGE_RELEASE "1%{?dist}")

# Автоматичне сканування Provides/Requires
set(CPACK_RPM_PACKAGE_AUTOREQ YES)
set(CPACK_RPM_PACKAGE_AUTOPROV YES)

# Ручні залежності
set(CPACK_RPM_PACKAGE_REQUIRES "openssl-libs >= 3.0.0, systemd")

# Включення релокабельності
set(CPACK_RPM_PACKAGE_RELOCATABLE ON)
