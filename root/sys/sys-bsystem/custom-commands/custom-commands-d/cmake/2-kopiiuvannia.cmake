add_executable(game_client src/main.cpp)
target_link_libraries(game_client PRIVATE SDL2::SDL2)

add_custom_command(
    TARGET game_client
    POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different
            "$<TARGET_FILE:SDL2::SDL2>"
            "$<TARGET_FILE_DIR:game_client>"
    COMMENT "Копіювання SDL2.dll до каталогу запуску"
    VERBATIM
)
