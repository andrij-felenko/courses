include(FetchContent)

# 1. Декларація: де взяти код та якої версії (не виконує мережевих запитів)
FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        10.2.1
    GIT_SHALLOW    TRUE
)

FetchContent_Declare(
    nlohmann_json
    URL            https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
    URL_HASH       SHA256=d6c65393116c3e981177ee7c99e917a226f74a056c703b4188b4eb14b5186b51
)

# 2. Матеріалізація: завантаження, підготовка та виклик add_subdirectory()
FetchContent_MakeAvailable(fmt nlohmann_json)

# 3. Використання: прямий зв'язок із рідними цілями бібліотек
add_executable(telemetry_daemon src/main.cpp)
target_link_libraries(telemetry_daemon PRIVATE
    fmt::fmt
    nlohmann_json::nlohmann_json
)
