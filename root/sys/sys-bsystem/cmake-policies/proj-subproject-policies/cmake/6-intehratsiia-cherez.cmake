# Попереднє налаштування для сторонніх репозиторіїв у FetchContent:
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
set(CMAKE_POLICY_DEFAULT_CMP0048 NEW)

FetchContent_Declare(
  legacy_lib
  GIT_REPOSITORY https://example.com/legacy_lib.git
  GIT_TAG v1.4.2
)
FetchContent_MakeAvailable(legacy_lib)
