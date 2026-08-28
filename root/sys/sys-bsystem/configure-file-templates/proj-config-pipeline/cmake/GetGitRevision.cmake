# cmake/GetGitRevision.cmake
# Модуль безпечного вилучення інформації про Git-ревізію

find_package(Git QUIET)

# Резервні значення на випадок збірки поза репозиторієм або без встановленого Git
set(DIAG_GIT_HASH "unknown")
set(DIAG_GIT_BRANCH "unknown")
set(DIAG_GIT_DIRTY_FLAG 0)

if(GIT_FOUND AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.git")
    # 1. Отримання 7-символьного скороченого SHA-1 поточного коміту
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" rev-parse --short=7 HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_hash_out
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _git_hash_res
    )
    if(_git_hash_res EQUAL 0 AND NOT "${_git_hash_out}" STREQUAL "")
        set(DIAG_GIT_HASH "${_git_hash_out}")
    endif()

    # 2. Отримання імені поточної гілки (або HEAD у разі detached state)
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" rev-parse --abbrev-ref HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_branch_out
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _git_branch_res
    )
    if(_git_branch_res EQUAL 0 AND NOT "${_git_branch_out}" STREQUAL "")
        set(DIAG_GIT_BRANCH "${_git_branch_out}")
    endif()

    # 3. Перевірка статусу робочого дерева на наявність незакомічених змін
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" status --porcelain
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_status_out
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _git_status_res
    )
    if(_git_status_res EQUAL 0 AND NOT "${_git_status_out}" STREQUAL "")
        # Якщо вивід не порожній, у дереві є змінені або додані файли
        set(DIAG_GIT_DIRTY_FLAG 1)
    endif()
else()
    # Якщо Git відсутній або папки .git немає (наприклад, збірка з tar.gz)
    set(DIAG_GIT_HASH "release-tarball")
    set(DIAG_GIT_BRANCH "release")
endif()
