# tests/CMakeLists.txt
enable_testing()

# Тест перевіряє, що виклик find_package успішно проходить у чистому середовищі
add_test(
    NAME test_find_fastcodec
    COMMAND ${CMAKE_COMMAND}
        -D CMAKE_MODULE_PATH=${CMAKE_CURRENT_SOURCE_DIR}/../cmake
        -D FastCodec_ROOT=${TEST_FASTCODEC_PREFIX}
        -P ${CMAKE_CURRENT_SOURCE_DIR}/test_find_fastcodec_script.cmake
)
