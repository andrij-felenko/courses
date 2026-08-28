cmake_minimum_required(VERSION 3.24)
project(NetworkService CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Пошук пакетів у дереві vcpkg_installed
find_package(fmt CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(OpenSSL REQUIRED)

add_executable(server src/main.cpp)

# Транзитивне зв'язування прапорців та каталогів заголовків
target_link_libraries(server PRIVATE
    fmt::fmt
    nlohmann_json::nlohmann_json
    OpenSSL::SSL
    OpenSSL::Crypto
)
