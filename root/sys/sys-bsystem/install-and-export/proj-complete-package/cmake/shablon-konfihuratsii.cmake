@PACKAGE_INIT@

# Підключення допоміжного макроса пошуку транзитивних залежностей
include(CMakeFindDependencyMacro)

# Підключення згенерованого файла імпортованих цілей
include("${CMAKE_CURRENT_LIST_DIR}/HyperionTargets.cmake")

# Перевірка наявності всіх обов'язкових компонентів
check_required_components(Hyperion)
