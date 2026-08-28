# 1. Перегляд динамічної секції ELF через readelf
readelf -d /path/to/myapp | grep -E '(RPATH|RUNPATH)'

# 2. Перегляд за допомогою утиліти objdump
objdump -p /path/to/myapp | grep -E '(RPATH|RUNPATH)'

# 3. Швидка заміна RPATH без перекомпільовування за допомогою patchelf
patchelf --set-rpath '$ORIGIN/../lib' /path/to/myapp

# 4. Повне очищення RPATH перед публікацією в системний репозиторій
patchelf --remove-rpath /path/to/myapp
