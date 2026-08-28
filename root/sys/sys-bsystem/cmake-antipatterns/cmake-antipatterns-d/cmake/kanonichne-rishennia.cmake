# ✅ Канонічний Modern CMake: явний контроль складу цілі
add_library(crypto_core STATIC)

target_sources(crypto_core
    PRIVATE
        src/aes.cpp
        src/sha256.cpp
        src/internal_keys.h
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/crypto/aes.h
            include/crypto/sha256.h
)
