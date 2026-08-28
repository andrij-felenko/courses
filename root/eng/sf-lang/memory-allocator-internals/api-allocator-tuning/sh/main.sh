# 1. Обмеження кількості арен для мінімізації споживання пам'яті в Docker
MALLOC_ARENA_MAX=2 ./backend_service

# 2. Фіксація порогу виділення через mmap на рівні 64 КіБ
MALLOC_MMAP_THRESHOLD_=65536 ./backend_service

# 3. Увімкнення суворої перевірки пошкодження цілісності купи (діагностика багів)
MALLOC_CHECK_=3 ./debug_binary

# 4. Тонке налаштування потокового кешу tcache через GLIBC_TUNABLES (glibc 2.34+)
GLIBC_TUNABLES="glibc.malloc.tcache_max=1024:glibc.malloc.tcache_count=16" ./app
