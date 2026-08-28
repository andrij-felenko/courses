# Варіант 1: Пошук встановленого пакета через vcpkg або системний менеджер
find_package(Microsoft.GSL CONFIG REQUIRED)
target_link_libraries(my_project PRIVATE Microsoft.GSL::GSL)

# Варіант 2: Автоматичне завантаження через FetchContent
include(FetchContent)
FetchContent_Declare(
    GSL
    GIT_REPOSITORY https://github.com/microsoft/GSL.git
    GIT_TAG        v4.0.0
)
FetchContent_MakeAvailable(GSL)
target_link_libraries(my_project PRIVATE Microsoft.GSL::GSL)
