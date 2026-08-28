var="file with spaces.txt"

# Варіант без лапок:
cat $var
# 1. Розгортання параметра: "cat file with spaces.txt"
# 2. Фаза Word Splitting розбиває рядок за IFS (пробіли) на 3 аргументи:
#    argv[1]="file", argv[2]="with", argv[3]="spaces.txt"
# 3. Виклик execve("cat", ["cat", "file", "with", "spaces.txt"]) -> ПОМИЛКА: файл "file" не знайдено.

# Варіант у подвійних лапках:
cat "$var"
# 1. Розгортання параметра відбувається всередині лапок: "cat file with spaces.txt"
# 2. Подвійні лапки блокують фази Word Splitting та Filename Expansion.
# 3. Фаза Quote Removal видаляє лапки.
# 4. Виклик execve("cat", ["cat", "file with spaces.txt"]) -> УСПІХ.
