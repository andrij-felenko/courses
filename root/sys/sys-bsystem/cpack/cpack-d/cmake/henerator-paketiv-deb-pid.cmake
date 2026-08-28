# Активація покомпонентного створення пакетів DEB
set(CPACK_DEB_COMPONENT_INSTALL ON)

# Метадані пакета
set(CPACK_DEBIAN_PACKAGE_SECTION "net")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Infrastructure Team <infra@example.com>")

# Автоматичне виявлення бібліотечних залежностей
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON)

# Явні системні залежності
set(CPACK_DEBIAN_PACKAGE_DEPENDS "libssl3 (>= 3.0.0), zlib1g")

# Зв'язок компонентів у DEB: dev-пакет залежить від runtime-пакета
set(CPACK_COMPONENT_DEVELOPMENT_DEPENDS "Runtime")
