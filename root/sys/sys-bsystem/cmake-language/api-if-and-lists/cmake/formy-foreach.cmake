set(NAMES  alice bob carol)
set(PORTS  8080  8081)

foreach(name port IN ZIP_LISTS NAMES PORTS)
  message(STATUS "${name} → ${port}")
endforeach()
# -- alice → 8080
# -- bob → 8081
# -- carol →              ← PORTS вичерпався, значення порожнє

foreach(x IN ZIP_LISTS NAMES PORTS)   # одне ім'я — CMake сам додасть суфікси
  message(STATUS "${x_0} → ${x_1}")
endforeach()
