# 1. Пошук URL-адрес та протоколів:
$ strings -a -n 8 binary | grep -Ei 'https?://|ftp://|wss?://'

# 2. Пошук IPv4 адрес:
$ strings -a -n 8 binary | grep -E '([0-9]{1,3}\.){3}[0-9]{1,3}'

# 3. Пошук шляхів файлової системи Linux:
$ strings -a -n 8 binary | grep -E '^/(etc|tmp|var|usr|dev|proc|sys)/'

# 4. Пошук шляхів вихідного коду компіляції:
$ strings -a -n 6 binary | grep -Ei '\.(c|cpp|cc|cxx|h|hpp|go|rs|py):[0-9]+'

# 5. Пошук ключів конфігурації CLI:
$ strings -a -n 4 binary | grep -E '^\-\-[a-zA-Z0-9_-]+'

# 6. Пошук 16-бітних UTF-16LE рядків (кросплатформний код або Windows-порти):
$ strings -a -n 8 -e l binary
