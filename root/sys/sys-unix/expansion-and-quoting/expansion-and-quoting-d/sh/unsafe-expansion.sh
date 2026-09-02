#!/usr/bin/env bash
# Чому незахищена змінна ламає навіть найпростіший тест.
set -u

show_argv() {
    printf 'команда отримала %d сл.' "$#"
    if [ "$#" -gt 0 ]; then
        printf ':'
        printf ' [%s]' "$@"
    fi
    printf '\n'
}

VAR=''

echo '--- що насправді бачить команда [ ---'
show_argv [ $VAR = admin ]     # слово зникло: аргументів чотири замість п'яти
show_argv [ "$VAR" = admin ]   # у лапках лишається порожнє, але СЛОВО

echo '--- і чим це закінчується ---'
if ( [ $VAR = admin ] ) 2>/dev/null; then
    echo 'збіг'
else
    printf 'тест провалився зі статусом %d, а ось його скарга:\n' "$?"
    ( [ $VAR = admin ] ) 2>&1 >/dev/null | sed 's/^/    /'
fi

echo '--- два робочих виправлення ---'
if [ "$VAR" = admin ]; then
    echo 'адмін'
else
    echo '[ "$VAR" = admin ] — чесне «ні», без помилки'
fi
if [[ $VAR == admin ]]; then
    echo 'адмін'
else
    echo '[[ … ]] не ділить слова й не глобить — лапки тут не обов’язкові'
fi

echo '--- той самий механізм в аргументах rm ---'
TARGET_DIR='/tmp/user data/output'
show_argv rm -rf $TARGET_DIR     # три аргументи: rm видалив би /tmp/user
show_argv rm -rf "$TARGET_DIR"   # один шлях, як і задумано

work=$(mktemp -d) || exit 1
trap 'rm -rf -- "$work"' EXIT
cd "$work" || exit 1
: > keep.txt
: > also-keep.log

TARGET='*'
echo 'а якщо у змінній опинилася маска:'
show_argv rm -rf $TARGET         # глобінг підставив УСІ файли каталогу
show_argv rm -rf "$TARGET"       # у лапках зірочка лишилася зірочкою
echo '(показано лише вектор argv[] — справжній rm тут не запускається)'
