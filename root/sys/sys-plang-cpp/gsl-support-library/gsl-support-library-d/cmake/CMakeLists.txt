# Підключення Microsoft GSL через CMake FetchContent
include(FetchContent)
FetchContent_Declare(
    GSL
    GIT_REPOSITORY https://github.com/microsoft/GSL.git
    GIT_TAG        v4.0.0
)
FetchContent_MakeAvailable(GSL)

add_executable(my_secure_service main.cpp)
target_link_libraries(my_secure_service PRIVATE Microsoft.GSL::GSL)
target_compile_features(my_secure_service PRIVATE cxx_std_20)
