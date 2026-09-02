#!/usr/bin/env bash
# Підстановка команд: вивід процесу стає текстом командного рядка.
set -u

work=$(mktemp -d) || exit 1
trap 'rm -rf -- "$work"' EXIT
mkdir -p "$work/project/src"
: > "$work/project/src/main.c"
file=$work/project/src/main.c

show_argv() {
    printf 'слів: %d' "$#"
    if [ "$#" -gt 0 ]; then
        printf ':'
        printf ' [%s]' "$@"
    fi
    printf '\n'
}

echo '--- гніздування сучасної форми $() ---'
# Три рівні вкладення — і жодного екранування: кожна пара дужок самодостатня.
root=$(dirname "$(dirname "$(realpath "$file")")")
printf 'корінь проєкту: %s\n' "$root"

echo '--- та сама робота застарілими апострофами ---'
# Уже на другому рівні потрібні зворотні слеші; на третьому їх треба подвоювати.
parent=`dirname \`realpath "$file"\``
printf 'батьківський каталог: %s\n' "$parent"

echo '--- кінцеві переводи рядка зрізаються ---'
raw=$(printf 'a\nb\n\n\n')
printf 'у результаті %d байти: %q\n' "${#raw}" "$raw"

echo '--- а внутрішні лишаються й дістаються поділу на слова ---'
show_argv $raw     # два слова: перевід рядка входить у типовий IFS
show_argv "$raw"   # одне слово: у лапках поділу немає

echo '--- статус завершення доступний як звичайно ---'
if ! out=$(ls "$work/no-such-dir" 2>&1); then
    printf 'команда всередині $() впала: %s\n' "$out"
fi

echo '--- підстановка процесів: аргументом стає шлях до каналу ---'
printf 'b\na\n' > "$work/one.txt"
printf 'a\nc\n' > "$work/two.txt"
# diff отримує два шляхи вигляду /dev/fd/N — жодного тимчасового файла.
diff -u <(sort "$work/one.txt") <(sort "$work/two.txt") || true
printf 'сам вираз <(…) розгортається у: %s\n' "$(echo <(true))"
