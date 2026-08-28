add_library(EngineCore STATIC
    src/UserSession.cpp
    src/Database.cpp
)

target_sources(EngineCore
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/Engine/UserSession.h
            include/Engine/Database.h
)

# Автоматична генерація тестового .cpp файлу для кожного заголовка у наборі
set_target_properties(EngineCore PROPERTIES
    VERIFY_INTERFACE_HEADER_SETS ON
)
