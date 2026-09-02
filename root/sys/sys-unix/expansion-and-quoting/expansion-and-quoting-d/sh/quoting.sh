#!/usr/bin/env bash
# Одна й та сама послідовність символів — без лапок, у подвійних і в одинарних.
set -u

work=$(mktemp -d) || exit 1
trap 'rm -rf -- "$work"' EXIT
cd "$work" || exit 1
: > 'my document.txt'
: > 'second file.txt'

# Друкує рівно те, що ядро побачило б у argv[] при execve(2).
show_argv() {
    printf 'слів: %d' "$#"
    if [ "$#" -gt 0 ]; then
        printf ':'
        printf ' [%s]' "$@"
    fi
    printf '\n'
}

name='my document.txt'

echo '--- без лапок: працюють і поділ на слова, і глобінг ---'
show_argv $name           # два слова: пробіл усередині значення розділив шлях
show_argv *.txt           # два слова: маску замінено іменами з каталогу

echo '--- подвійні лапки: розгортання є, поділу й глобінгу немає ---'
show_argv "$name"         # одне слово — саме те, що треба команді
show_argv "*.txt"         # одне слово: маска лишилася звичайним текстом
show_argv "$HOME/*.txt"   # змінну розгорнуто, маску — ні

echo '--- одинарні лапки: не розгортається нічого ---'
show_argv '$HOME *.txt $(date) $((6*7))'

echo '--- зворотний слеш захищає рівно один наступний символ ---'
show_argv \$HOME \*.txt hello\ world

echo '--- одинарна лапка всередині одинарних лапок ---'
# Блок закривають, підставляють екрановану лапку й відкривають знову.
show_argv 'It'\''s working'
show_argv "It's working"     # у подвійних лапках вона просто символ

echo '--- порожнє значення: без лапок слово зникає з argv[] ---'
empty=
show_argv a $empty b      # два слова
show_argv a "$empty" b    # три слова, середнє порожнє

echo '--- ANSI-C цитування $(...) з апострофом ---'
show_argv $'колонка1\tколонка2'
printf 'байт ESC із $\x27\\x1b\x27: ' ; printf '%s' $'\x1b' | od -An -tx1
