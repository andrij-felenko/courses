set(OPTIMIZATION_LEVEL "-O3" CACHE STRING "Рівень оптимізації")

function(build_target)
    # Створюємо локальну змінну з таким самим ім'ям
    set(OPTIMIZATION_LEVEL "-O0")
    
    # Звичайне розіменування: повертає локальне значення "-O0"
    message(STATUS "Локальний рівень: ${OPTIMIZATION_LEVEL}")
    
    # Пряме звернення до кешу: повертає глобальне значення "-O3"
    message(STATUS "Глобальний рівень кешу: $CACHE{OPTIMIZATION_LEVEL}")
endfunction()

build_target()
