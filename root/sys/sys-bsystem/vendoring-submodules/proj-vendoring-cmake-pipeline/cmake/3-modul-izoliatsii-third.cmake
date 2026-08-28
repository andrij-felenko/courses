# third_party/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)

# Політика CMP0077: локальні змінні set() перемагають чужі option() без FORCE
if(POLICY CMP0077)
    cmake_policy(SET CMP0077 NEW)
endif()

# 1. Попереднє перекриття опцій кешу стороннього підпроєкту
set(BUILD_TESTS OFF)
set(BUILD_TESTING OFF)
set(TINYXML2_BUILD_TESTING OFF)
set(BUILD_SHARED_LIBS OFF)

# 2. Підключення бібліотеки TinyXML2
# EXCLUDE_FROM_ALL: відсікає всі сторонні цілі від дефолтної збірки all
# SYSTEM: позначає відкриті заголовки як системні (-isystem), придушуючи попередження
add_subdirectory(tinyxml2 EXCLUDE_FROM_ALL SYSTEM)

# Створюємо стандартизований псевдонім простору імен, якщо бібліотека його не створила
if(TARGET tinyxml2 AND NOT TARGET Vendor::TinyXML2)
    add_library(Vendor::TinyXML2 ALIAS tinyxml2)
endif()

# 3. Підключення Miniz (чисті C-файли без власного CMakeLists.txt)
# Створюємо власну статичну ціль з інкапсульованими вимогами вжитку
add_library(miniz_static STATIC
    "${CMAKE_CURRENT_SOURCE_DIR}/miniz/miniz.c"
)

# Експортуємо системні каталоги заголовків для споживачів
target_include_directories(miniz_static
    SYSTEM PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/miniz>"
)

# Вимикаємо діагностику компілятора для старої кодової бази C
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(miniz_static PRIVATE -w)
elseif(MSVC)
    target_compile_options(miniz_static PRIVATE /w)
endif()

# Реєструємо псевдонім простору імен
add_library(Vendor::Miniz ALIAS miniz_static)
