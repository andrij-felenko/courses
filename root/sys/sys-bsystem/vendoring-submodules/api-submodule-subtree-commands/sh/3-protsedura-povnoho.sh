# Крок 1. Деініціалізація підмодуля (очищення .git/config та робочих файлів)
git submodule deinit -f third_party/fmt

# Крок 2. Видалення запису з індексу Git та файлу .gitmodules
git rm -f third_party/fmt

# Крок 3. Видалення фізичного сховища об'єктів підмодуля (запобігає засміченню .git)
rm -rf .git/modules/third_party/fmt

# Крок 4. Фіксація змін у батьківському репозиторії
git commit -m "Remove fmt submodule from third_party"

# Крок 5. Перевірка відсутності залишкових записів
git status
