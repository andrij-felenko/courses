# cmake/ProjectLibrary.cmake
include_guard(GLOBAL)
include(GNUInstallDirs)

function(add_project_library)
  set(options     NO_INSTALL)
  set(oneValue    NAME OUT_TARGET)
  set(multiValue  SOURCES PUBLIC_HEADERS PUBLIC_DEPS PRIVATE_DEPS)
  cmake_parse_arguments(PARSE_ARGV 0 ARG "${options}" "${oneValue}" "${multiValue}")

  # ── 1. Скарги на виклик ───────────────────────────────────────────────
  if(DEFINED ARG_UNPARSED_ARGUMENTS)
    string(JOIN ", " known ${options} ${oneValue} ${multiValue})
    message(FATAL_ERROR
      "add_project_library: не розпізнано «${ARG_UNPARSED_ARGUMENTS}».\n"
      "  Відомі ключові слова: ${known}")
  endif()

  if(DEFINED ARG_KEYWORDS_MISSING_VALUES)
    message(FATAL_ERROR
      "add_project_library: після «${ARG_KEYWORDS_MISSING_VALUES}» не вказано жодного значення.")
  endif()

  if(NOT DEFINED ARG_NAME)
    message(FATAL_ERROR "add_project_library: обов'язковий аргумент NAME <ім'я бібліотеки>.")
  endif()

  if(NOT DEFINED ARG_SOURCES)
    message(FATAL_ERROR "add_project_library(${ARG_NAME}): обов'язковий аргумент SOURCES <файли…>.")
  endif()

  if(TARGET "${ARG_NAME}")
    message(FATAL_ERROR "add_project_library: ціль «${ARG_NAME}» уже існує.")
  endif()

  # ── 2. Ціль ───────────────────────────────────────────────────────────
  set(target "${ARG_NAME}")
  add_library("${target}" ${ARG_SOURCES})
  add_library("proj::${target}" ALIAS "${target}")

  target_compile_features("${target}" PUBLIC cxx_std_20)
  set_target_properties("${target}" PROPERTIES
    OUTPUT_NAME              "proj_${target}"
    POSITION_INDEPENDENT_CODE ON)

  if(DEFINED ARG_PUBLIC_HEADERS)
    target_sources("${target}" PUBLIC
      FILE_SET HEADERS
      BASE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/include"
      FILES ${ARG_PUBLIC_HEADERS})
  endif()

  foreach(dep IN LISTS ARG_PUBLIC_DEPS)
    target_link_libraries("${target}" PUBLIC "${dep}")
  endforeach()

  foreach(dep IN LISTS ARG_PRIVATE_DEPS)
    target_link_libraries("${target}" PRIVATE "${dep}")
  endforeach()

  # ── 3. Встановлення ───────────────────────────────────────────────────
  if(NOT ARG_NO_INSTALL)
    set(headerArgs "")
    if(DEFINED ARG_PUBLIC_HEADERS)
      set(headerArgs FILE_SET HEADERS DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
    endif()
    install(TARGETS "${target}" EXPORT projTargets
      ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
      LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
      RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
      ${headerArgs})
  endif()

  # ── 4. Результат ──────────────────────────────────────────────────────
  set_property(GLOBAL APPEND PROPERTY PROJ_LIBRARIES "proj::${target}")

  if(DEFINED ARG_OUT_TARGET)
    set("${ARG_OUT_TARGET}" "proj::${target}" PARENT_SCOPE)
  endif()
endfunction()
