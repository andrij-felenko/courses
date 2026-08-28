# У файлі тулчейна або CMakeLists.txt
if(CMAKE_CROSSCOMPILING)
    find_program(QEMU_ARM_EMULATOR NAMES qemu-aarch64-static qemu-aarch64)
    if(QEMU_ARM_EMULATOR)
        # Вказуємо шлях до цільового sysroot для пошуку динамічних бібліотек .so
        set(CMAKE_CROSSCOMPILING_EMULATOR
            "${QEMU_ARM_EMULATOR}"
            "-L" "${CMAKE_SYSROOT}"
        )
    endif()
endif()

# Оголошення тесту в CMake
enable_testing()
add_executable(unit_tests tests/test_main.cpp)
add_test(NAME CoreAlgorithmTests COMMAND unit_tests)
