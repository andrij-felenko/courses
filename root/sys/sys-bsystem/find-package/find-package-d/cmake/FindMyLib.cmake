# cmake/FindMyLib.cmake
include(FindPackageHandleStandardArgs)

# 1. Пошук заголовків
find_path(MyLib_INCLUDE_DIR
    NAMES mylib/mylib.h
    PATH_SUFFIXES include
)

# 2. Пошук компільованої бібліотеки
find_library(MyLib_LIBRARY
    NAMES mylib libmylib
    PATH_SUFFIXES lib lib64
)

# 3. Видобування версії із заголовка (опціонально)
if(MyLib_INCLUDE_DIR AND EXISTS "${MyLib_INCLUDE_DIR}/mylib/mylib.h")
    file(STRINGS "${MyLib_INCLUDE_DIR}/mylib/mylib.h" _ver_line
         REGEX "^#define[ \t]+MYLIB_VERSION[ \t]+\"[^\"]+\"")
    string(REGEX MATCH "\"([^\"]+)\"" _ "${_ver_line}")
    set(MyLib_VERSION "${CMAKE_MATCH_1}")
    unset(_ver_line)
endif()

# 4. Стандартизована перевірка знайдених змінних
find_package_handle_standard_args(MyLib
    REQUIRED_VARS MyLib_LIBRARY MyLib_INCLUDE_DIR
    VERSION_VAR MyLib_VERSION
)

# 5. Створення імпортованої цілі
if(MyLib_FOUND AND NOT TARGET MyLib::MyLib)
    add_library(MyLib::MyLib UNKNOWN IMPORTED)
    set_target_properties(MyLib::MyLib PROPERTIES
        IMPORTED_LOCATION "${MyLib_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${MyLib_INCLUDE_DIR}"
    )
endif()

# 6. Забезпечення зворотної сумісності для старих проєктів
if(MyLib_FOUND)
    set(MyLib_INCLUDE_DIRS "${MyLib_INCLUDE_DIR}")
    set(MyLib_LIBRARIES "${MyLib_LIBRARY}")
endif()

mark_as_advanced(MyLib_INCLUDE_DIR MyLib_LIBRARY)
