cmake_minimum_required(VERSION 3.1)
project(ModernCppApp LANGUAGES CXX)

add_executable(my_service
    src/main.cpp
    src/network.cpp
    src/dispatcher.cpp
)

# Встановлення стандарту C++14 для цільового бінарника
set_target_properties(my_service PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

# Додавання системних багатопотокових бібліотек
find_package(Threads REQUIRED)
target_link_libraries(my_service PRIVATE Threads::Threads)
