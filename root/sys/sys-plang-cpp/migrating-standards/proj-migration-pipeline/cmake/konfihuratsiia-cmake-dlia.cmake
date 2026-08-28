# Опція увімкнення санітайзерів
option(ENABLE_SANITIZERS "Увімкнути ASan, UBSan та LSan" OFF)

if(ENABLE_SANITIZERS)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        message(STATUS "Увімкнено санітайзери: AddressSanitizer, UndefinedBehaviorSanitizer")
        
        # Прапорці компіляції для точного відстеження стека
        set(SANITIZER_FLAGS "-fsanitize=address,undefined -fno-omit-frame-pointer -g -O1")
        
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${SANITIZER_FLAGS}")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${SANITIZER_FLAGS}")
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${SANITIZER_FLAGS}")
        set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${SANITIZER_FLAGS}")
    else()
        message(WARNING "Санітайзери підтримуються лише на компіляторах GCC та Clang")
    endif()
endif()
