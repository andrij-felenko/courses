add_library(core src/core.cpp src/detail.cpp)
add_library(proj::core ALIAS core)
target_sources(core PUBLIC
  FILE_SET HEADERS BASE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/include"
  FILES include/proj/core.hpp)
target_link_libraries(core PUBLIC fmt::fmt)
target_link_libraries(core PRIVATE Threads::Threads)
target_compile_features(core PUBLIC cxx_std_20)
set_target_properties(core PROPERTIES OUTPUT_NAME "proj_core" POSITION_INDEPENDENT_CODE ON)
install(TARGETS core EXPORT projTargets
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
  FILE_SET HEADERS DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
