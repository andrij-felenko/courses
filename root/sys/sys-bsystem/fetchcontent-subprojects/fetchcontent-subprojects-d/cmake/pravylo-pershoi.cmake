# Кореневий CMakeLists.txt проєкту my_app
include(FetchContent)

# Головний проєкт явно фіксує єдину узгоджену версію spdlog для ВСІХ підпроєктів
FetchContent_Declare(
    spdlog
    GIT_REPOSITORY https://github.com/gabime/spdlog.git
    GIT_TAG        v1.13.0
)

# Оголошуємо модулі проєкту
FetchContent_Declare(audio_engine   GIT_REPOSITORY ... GIT_TAG v2.0)
FetchContent_Declare(network_client GIT_REPOSITORY ... GIT_TAG v1.5)

# Активація
FetchContent_MakeAvailable(spdlog audio_engine network_client)
