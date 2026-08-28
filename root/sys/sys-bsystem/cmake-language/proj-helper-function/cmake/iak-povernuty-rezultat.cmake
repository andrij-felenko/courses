function(compute_paths)
  block(PROPAGATE inc_dir lib_dir)
    set(root "${CMAKE_CURRENT_SOURCE_DIR}/dist")   # службова, назовні не поїде
    set(inc_dir "${root}/include")
    set(lib_dir "${root}/lib")
  endblock()
  # тут inc_dir і lib_dir уже є, root — немає
  set(inc_dir "${inc_dir}" PARENT_SCOPE)
  set(lib_dir "${lib_dir}" PARENT_SCOPE)
endfunction()
