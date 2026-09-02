#!/usr/bin/env bash
# Фаза 5: розгортання імен файлів. Усе відбувається у тимчасовій теці.
set -u
shopt -s extglob          # розширені маски ?() *() +() @() !()

work=$(mktemp -d) || exit 1
trap 'rm -rf -- "$work"' EXIT
cd "$work" || exit 1

mkdir -p src/deep
: > notes.txt
: > readme.md
: > build.log
: > core.dump
: > .hidden
: > data1.csv
: > data2.csv
: > src/main.c
: > src/util.c
: > src/deep/extra.c

show_argv() {
    printf 'слів: %d' "$#"
    if [ "$#" -gt 0 ]; then
        printf ':'
        printf ' [%s]' "$@"
    fi
    printf '\n'
}

echo '--- прості маски ---'
show_argv *.csv
show_argv data?.csv       # ? — рівно один символ
show_argv [bn]*           # множина символів
show_argv *               # .hidden сюди не потрапляє: провідна крапка захищена
show_argv .*              # крапку треба написати явно; сюди входять і . та ..

echo '--- зірочка не переходить межу каталогу ---'
show_argv src/*.c         # два файли
show_argv src/*/*.c       # рівень нижче доводиться називати окремим сегментом
shopt -s globstar
show_argv src/**/*.c      # ** обходить підкаталоги рекурсивно
shopt -u globstar

echo '--- розширені маски: усе, крім тексту й розмітки ---'
show_argv !(*.txt|*.md)
echo 'видаляємо саме ці файли (каталог src лишаємо):'
rm -f -- !(*.txt|*.md|src)
echo 'лишилося:'
ls -A

echo '--- коли збігів немає ---'
show_argv *.nonexistent              # POSIX: маска лишається буквально
shopt -s nullglob
show_argv *.nonexistent              # nullglob: жодного слова
shopt -u nullglob
if ( shopt -s failglob; show_argv *.nonexistent ); then
    echo 'збіг знайдено'
else
    echo 'failglob: оболонка відмовилася виконувати команду'
fi
