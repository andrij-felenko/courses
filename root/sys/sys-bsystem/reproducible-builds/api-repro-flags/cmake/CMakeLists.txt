# Перевірка та конфігурація компіляторів GCC і Clang
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    # Перетворення абсолютних шляхів на відносні
    add_compile_options(
        -ffile-prefix-map=${CMAKE_SOURCE_DIR}=.
        -ffile-prefix-map=${CMAKE_BINARY_DIR}=.
        -fno-ident
        -gno-record-gcc-switches
    )
    # Детерміністичний Build ID для компонувальника
    add_link_options("-Wl,--build-id=sha1")
endif()

# Налаштування для середовища MSVC на Windows
if(MSVC)
    add_compile_options(/experimental:deterministic "/pathmap:${CMAKE_SOURCE_DIR}=.")
    add_link_options(/Brepro "/PDBALTPATH:%_PDB%")
endif()

# Детерміністичний виклик архіватора статичних бібліотек
set(CMAKE_C_ARCHIVE_CREATE "<CMAKE_AR> Dqc <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_C_ARCHIVE_APPEND "<CMAKE_AR> Dq  <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_C_ARCHIVE_FINISH "<CMAKE_RANLIB> -D <TARGET>")

set(CMAKE_CXX_ARCHIVE_CREATE "<CMAKE_AR> Dqc <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_CXX_ARCHIVE_APPEND "<CMAKE_AR> Dq  <TARGET> <LINK_FLAGS> <OBJECTS>")
set(CMAKE_CXX_ARCHIVE_FINISH "<CMAKE_RANLIB> -D <TARGET>")
