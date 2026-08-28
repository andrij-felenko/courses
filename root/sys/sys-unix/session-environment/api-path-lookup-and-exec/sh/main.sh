# 1. type — внутрішній аналізатор Bash (показує alias, builtin, function чи file)
$ type ls
ls is aliased to `ls --color=auto'

$ type cd
cd is a shell builtin

$ type grep
grep is hashed (/usr/bin/grep)

# 2. type -a — виводить УСІ можливі збіги в PATH, аліасах та вбудованих елементах
$ type -a echo
echo is a shell builtin
echo is /usr/bin/echo

# 3. command -v — стандартний POSIX-спосіб визначення типу команди (для використання у скриптах)
$ command -v git
/usr/bin/git

# 4. builtin — виклики команди, ігноруючи однойменні функції або псевдоніми
$ builtin cd /tmp

# 5. which — зовнішня утиліта (або builtin у zsh), яка шукає виключно у PATH
$ which grep
/usr/bin/grep

# 6. whereis — шукає бінарники, вихідні коди та man-сторінки у системних каталогах
$ whereis ls
ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
