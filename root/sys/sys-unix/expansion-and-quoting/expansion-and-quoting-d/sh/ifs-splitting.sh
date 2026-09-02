#!/usr/bin/env bash
# Фаза 4: поділ на слова. Ділить ЛИШЕ результати підстановок і лише поза лапками.
set -u

show_argv() {
    printf 'слів: %d' "$#"
    if [ "$#" -gt 0 ]; then
        printf ':'
        printf ' [%s]' "$@"
    fi
    printf '\n'
}

line='  root:x:0:0::/root:/bin/bash  '

echo '--- типовий IFS: пробіл, табуляція, новий рядок ---'
show_argv $line     # одне слово: двокрапка не роздільник, крайні пробіли зникли
show_argv "$line"   # у лапках поділу немає взагалі — пробіли на місці

echo '--- IFS=":" — небілий роздільник ---'
old_ifs=$IFS
IFS=:
# Тепер пробіли частиною роздільника не є: вони лишаються всередині слів,
# а порожнє поле між двома двокрапками дає порожнє слово.
show_argv $line
IFS=$old_ifs

echo '--- IFS="" вимикає поділ повністю ---'
IFS=''
show_argv $line
IFS=$old_ifs

echo '--- розбір /etc/passwd рядок за рядком ---'
passwd_file=/etc/passwd
sample=''
if [ ! -r "$passwd_file" ]; then
    echo "немає доступу до $passwd_file — беремо вбудований зразок" >&2
    sample=$(mktemp) || exit 1
    trap 'rm -f -- "$sample"' EXIT
    cat > "$sample" <<'EOF'
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
EOF
    passwd_file=$sample
fi

printf '%-12s %-6s %s\n' КОРИСТУВАЧ UID ОБОЛОНКА
# IFS=: перед read діє ЛИШЕ на цю команду — глобальне значення лишається цілим.
# -r забороняє read тлумачити зворотний слеш як екран.
while IFS=: read -r user _pass uid _gid _gecos _home shell; do
    case $user in
        '' | \#*) continue ;;   # порожні рядки й коментарі
    esac
    case $uid in
        '' | *[!0-9]*) continue ;;   # зіпсований рядок пропускаємо мовчки
    esac
    [ "$uid" -lt 5 ] || continue
    printf '%-12s %-6s %s\n' "$user" "$uid" "$shell"
done < "$passwd_file"

printf 'глобальний IFS не постраждав: %s\n' "$([ "$IFS" = "$old_ifs" ] && echo так || echo ні)"
