# cmake/MyLibConfig.cmake.in
@PACKAGE_INIT@

# Підключення транзитивних залежностей (якщо є)
include(CMakeFindDependencyMacro)
# find_dependency(ZLIB 1.2 REQUIRED)

# Підключення згенерованого експортного набору цілей
include("${CMAKE_CURRENT_LIST_DIR}/MyLibTargets.cmake")

# Перевірка наявності запитаних компонентів
check_required_components(MyLib)
