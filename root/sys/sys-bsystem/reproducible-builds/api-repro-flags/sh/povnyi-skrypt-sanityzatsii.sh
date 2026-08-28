#!/usr/bin/env bash
set -euo pipefail

# 1. Примусове встановлення канонічної локалі для передбачуваного сортування рядків
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export LC_COLLATE=C

# 2. Фіксація часового поясу в нульовий меридіан
export TZ=UTC

# 3. Нормалізація маски створення файлів
umask 0022

# 4. Встановлення фіксованого часу коміту для компіляторів та архіваторів
export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct 2>/dev/null || echo 1700000000)

# 5. Примусовий детермінізм для GNU binutils
export ZERO_AR_DATE=1

# 6. Очищення шляхів пошуку бінарних файлів від локальних каталогів користувача
export PATH="/usr/bin:/bin:/usr/local/bin"

# 7. Видалення небезпечних змінних середовища
unset LD_PRELOAD
unset LD_LIBRARY_PATH
unset C_INCLUDE_PATH
unset CPLUS_INCLUDE_PATH
unset TMPDIR

# 8. Запуск збірки
cmake --preset release
cmake --build --preset release
