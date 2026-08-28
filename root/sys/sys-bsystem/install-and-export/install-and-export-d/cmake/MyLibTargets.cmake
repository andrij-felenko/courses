# Фрагмент згенерованого MyLibTargets.cmake
add_library(MyLib::mylib_core SHARED IMPORTED)

set_target_properties(MyLib::mylib_core PROPERTIES
  INTERFACE_COMPILE_FEATURES "cxx_std_20"
  INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
)

# Підключення конфігураційного файла для конкретного типу збірки (Release/Debug)
include("${CMAKE_CURRENT_LIST_DIR}/MyLibTargets-release.cmake")
