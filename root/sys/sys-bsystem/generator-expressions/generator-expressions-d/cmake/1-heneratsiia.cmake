file(GENERATE
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/genex_diag_$<CONFIG>.txt"
    CONTENT "Активна конфігурація: $<CONFIG>
Платформа: $<PLATFORM_ID>
Компілятор CXX: $<CXX_COMPILER_ID> версії $<CXX_COMPILER_VERSION>
Файл артефакту core: $<TARGET_FILE:core>
Прапорці компіляції: $<TARGET_PROPERTY:core,COMPILE_OPTIONS>
Каталоги включення: $<TARGET_PROPERTY:core,INCLUDE_DIRECTORIES>
"
)
