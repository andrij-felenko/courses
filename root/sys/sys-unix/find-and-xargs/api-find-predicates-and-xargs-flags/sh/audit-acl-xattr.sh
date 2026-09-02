#!/usr/bin/env bash
# Аудит розширених метаданих дерева: нетривіальні POSIX ACL, спадкові
# default ACL на каталогах, SUID/SGID та Linux capabilities.
#
# Дерево обходимо РІВНО один раз: `find -printf '%y\t%M\t%p\0'` віддає тип,
# права й шлях, а далі xargs -0 роздає готові списки пакетами утилітам
# acl (getfacl) та libcap (getcap).
set -euo pipefail
export LC_ALL=C   # діагностику утиліт розбираємо нижче, вона має бути англійською

self_dir=$(cd -- "$(dirname -- "$0")" && pwd)
# shellcheck source=lib/common.sh
. "$self_dir/lib/common.sh"

usage() {
    cat >&2 <<'EOF'
використання: audit-acl-xattr.sh [-x] КОРІНЬ [КОРІНЬ...]
  -x   не перетинати межі файлової системи (find -xdev)
EOF
    exit 2
}

# Масив ніколи не порожній — інакше "${find_opts[@]}" під `set -u` на старих
# bash розгортався б у помилку.
find_opts=(-ignore_readdir_race)   # файл, що зник під час обходу, — не помилка
while getopts ':xh' opt; do
    case $opt in
        x) find_opts+=(-xdev) ;;
        h) usage ;;
        *) die "невідомий прапорець -$OPTARG" ;;
    esac
done
shift $((OPTIND - 1))
(( $# >= 1 )) || usage
roots=("$@")

need find xargs grep sed tr wc
require_gnu find xargs grep

have_acl=0
if command -v getfacl >/dev/null 2>&1; then have_acl=1; fi
have_cap=0
if command -v getcap >/dev/null 2>&1; then have_cap=1; fi

make_tmpdir
errlog="$SELF_TMPDIR/errors"; : >"$errlog"

# --- 1. Єдиний обхід -------------------------------------------------------
tree="$SELF_TMPDIR/tree"
# Розділювач записів — NUL: у назві файлу законний будь-який байт, крім '/'
# і '\0', тож '\n' як межа запису тут не годиться.
find_rc=0
find "${roots[@]}" "${find_opts[@]}" -printf '%y\t%M\t%p\0' \
    >"$tree" 2>"$errlog" || find_rc=$?
if (( find_rc != 0 )); then
    warn "find повернув $find_rc: частина дерева недоступна (EACCES або зниклі вузли)"
fi
if [[ -s $errlog ]]; then
    warn "повідомлень find у stderr: $(wc -l <"$errlog")"
fi

files="$SELF_TMPDIR/files"
dirs="$SELF_TMPDIR/dirs"
suid="$SELF_TMPDIR/suid"

# Тримаємо три дескриптори відкритими, а не переоткриваємо файл на кожен
# запис: інакше на великому дереві левову частку часу з'їдає open()/close().
exec 3>"$files" 4>"$dirs" 5>"$suid"

total=0
lsm_hint=0
while IFS=$'\t' read -r -d '' type mode path; do
    total=$((total + 1))
    case $type in
        f) printf '%s\0' "$path" >&3 ;;
        d) printf '%s\0' "$path" >&4 ;;
    esac
    # SUID/SGID видно прямо в рядку прав: 's' або 'S' на позиціях 3 і 6
    # (нумерація з нуля), тобто там, де в 'rwx' стоїть біт виконання.
    if [[ $type == f ]] && [[ ${mode:3:1} == [sS] || ${mode:6:1} == [sS] ]]; then
        printf '%s\t%s\0' "$mode" "$path" >&5
    fi
    # 11-й символ %M ('+' або '.') — лише підказка про розширені метадані:
    # заповнюють його не всі збірки, тож остаточне слово нижче за getfacl.
    if [[ ${mode:10:1} == '.' ]]; then
        lsm_hint=$((lsm_hint + 1))
    fi
done <"$tree"

exec 3>&- 4>&- 5>&-

# --- 2. Нетривіальні POSIX ACL --------------------------------------------
acl_list="$SELF_TMPDIR/acl.txt"; : >"$acl_list"
def_list="$SELF_TMPDIR/defacl.txt"; : >"$def_list"
acl_nul="$SELF_TMPDIR/acl.nul"; : >"$acl_nul"

if (( have_acl )); then
    raw="$SELF_TMPDIR/facl.access"
    rc=0
    # -s (--skip-base) лишає у виводі лише ті шляхи, де є записи понад базові
    # user::/group::/other::, тобто справжній ACL; -p не зрізає провідний '/'.
    xargs -0 -a "$files" -r -n 200 getfacl -s -p -- \
        >"$raw" 2>>"$errlog" || rc=$?
    explain_xargs_status "$rc" || warn "getfacl (access) відпрацював не на всіх пакетах"
    # Вивід getfacl рядковий: ім'я з '\n' він передати не може — це межа
    # утиліти acl, і саме тому власний список шляхів у нас NUL-розділений.
    sed -n 's/^# file: //p' "$raw" >"$acl_list"
    tr '\n' '\0' <"$acl_list" >"$acl_nul"

    raw_d="$SELF_TMPDIR/facl.default"
    rc=0
    xargs -0 -a "$dirs" -r -n 200 getfacl -d -s -p -- \
        >"$raw_d" 2>>"$errlog" || rc=$?
    explain_xargs_status "$rc" || warn "getfacl (default) відпрацював не на всіх пакетах"
    sed -n 's/^# file: //p' "$raw_d" >"$def_list"
fi

printf '== файли з нетривіальним POSIX ACL ==\n'
if (( have_acl )); then
    if [[ -s $acl_list ]]; then
        sed 's/^/  /' "$acl_list"
    else
        printf '  немає\n'
    fi
else
    printf '  getfacl відсутній (пакет acl) — розділ пропущено\n'
fi

printf '\n== каталоги зі спадковим default ACL ==\n'
if (( have_acl )); then
    if [[ -s $def_list ]]; then
        sed 's/^/  /' "$def_list"
    else
        printf '  немає\n'
    fi
else
    printf '  getfacl відсутній (пакет acl) — розділ пропущено\n'
fi

# --- 3. SUID/SGID, окремо позначені ті, що мають ще й ACL ------------------
printf '\n== SUID/SGID файли ==\n'
suid_n=0
suid_acl=0
while IFS=$'\t' read -r -d '' mode path; do
    suid_n=$((suid_n + 1))
    mark=' '
    if (( have_acl )) && grep -zqxF -e "$path" "$acl_nul"; then
        mark='+'
        suid_acl=$((suid_acl + 1))
    fi
    # %q екранує керуючі символи в імені: інакше файл із '\n' або з ESC
    # у назві поламав би вивід аудиту (а то й термінал).
    printf '  %s%s  %q\n' "$mode" "$mark" "$path"
done <"$suid"
if (( suid_n == 0 )); then
    printf '  немає\n'
fi

# --- 4. Linux capabilities -------------------------------------------------
printf '\n== файли з Linux capabilities ==\n'
if (( have_cap )); then
    caps="$SELF_TMPDIR/caps"
    rc=0
    # getcap мовчить про файли без capabilities, тож у виводі лишається
    # тільки суть; пакетуємо по 200 шляхів, щоб не платити за fork на кожен.
    xargs -0 -a "$files" -r -n 200 getcap >"$caps" 2>>"$errlog" || rc=$?
    explain_xargs_status "$rc" || warn "getcap відпрацював не на всіх пакетах"
    if [[ -s $caps ]]; then
        sed 's/^/  /' "$caps"
    else
        printf '  немає\n'
    fi
else
    printf '  getcap відсутній (пакет libcap) — розділ пропущено\n'
fi

# --- 5. Підсумок -----------------------------------------------------------
printf '\n== підсумок ==\n'
printf '  вузлів обійдено:            %s\n' "$total"
printf '  файлів / каталогів:         %s / %s\n' \
    "$(nul_count "$files")" "$(nul_count "$dirs")"
printf '  з міткою LSM у %%M (підказка): %s\n' "$lsm_hint"
printf '  з нетривіальним ACL:        %s\n' "$(wc -l <"$acl_list")"
printf '  каталогів з default ACL:    %s\n' "$(wc -l <"$def_list")"
printf '  SUID/SGID (з них із ACL):   %s (%s)\n' "$suid_n" "$suid_acl"
if [[ -s $errlog ]]; then
    printf '  помилки обходу — у %s\n' "$errlog"
    # Тека гине разом із trap на EXIT, тож копію лишаємо поруч зі скриптом.
    cp -- "$errlog" ./audit-errors.log && printf '  копія: ./audit-errors.log\n'
fi
