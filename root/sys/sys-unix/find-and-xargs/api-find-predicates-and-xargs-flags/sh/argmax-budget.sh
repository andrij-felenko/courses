#!/usr/bin/env bash
# Скільки шляхів улізе в один execve(): рахуємо бюджет аргументів за формулою
#
#   бюджет = ARG_MAX - розмір(environ) - розмір(покажчиків) - 2048
#
# передбачаємо кількість пакетів для реального дерева і звіряємо передбачення
# з тим, як насправді поділив аргументи xargs.
set -euo pipefail
# Рахуємо БАЙТИ, а не символи: у UTF-8-локалі ${#s} для кириличного імені дав
# би вдвічі менше, ніж копіює ядро.
export LC_ALL=C

self_dir=$(cd -- "$(dirname -- "$0")" && pwd)
# shellcheck source=lib/common.sh
. "$self_dir/lib/common.sh"

usage() {
    cat >&2 <<'EOF'
використання: argmax-budget.sh КОРІНЬ
  Обходить КОРІНЬ, рахує бюджет аргументів execve(), передбачає кількість
  запусків і порівнює передбачення з фактичною поведінкою xargs.
EOF
    exit 2
}

(( $# == 1 )) || usage
root=$1
[[ -d $root ]] || die "не каталог: $root"

need find xargs getconf env tr wc sed awk head
require_gnu find xargs env

make_tmpdir

# --- 1. Системні ліміти ----------------------------------------------------
arg_max=$(getconf ARG_MAX)
page=$(getconf PAGE_SIZE)
max_arg_strlen=$((32 * page))        # fs/exec.c: MAX_ARG_STRLEN = 32 * PAGE_SIZE
ptr=$(( $(getconf LONG_BIT) / 8 ))   # sizeof(char *)
reserve=2048                         # резерв POSIX під auxv і вирівнювання стеку

printf '== системні ліміти ==\n'
printf '  ARG_MAX (sysconf _SC_ARG_MAX): %s байтів\n' "$arg_max"
printf '  PAGE_SIZE %s → MAX_ARG_STRLEN = 32·PAGE_SIZE = %s байтів (%s КіБ)\n' \
    "$page" "$max_arg_strlen" "$((max_arg_strlen / 1024))"
printf '  sizeof(char *): %s байтів\n' "$ptr"

stack=$(ulimit -s)
if [[ $stack == unlimited ]]; then
    printf '  RLIMIT_STACK: unlimited → ядро бере стелю 3/4·_STK_LIM\n'
elif [[ $stack =~ ^[0-9]+$ ]]; then
    printf '  RLIMIT_STACK: %s КіБ → чверть стеку = %s байтів\n' \
        "$stack" "$((stack * 1024 / 4))"
fi

# --- 2. Скільки з'їдає оточення -------------------------------------------
# `env -0` друкує кожну змінну з термінатором NUL, тож кількість байтів — це
# рівно сума strlen(var)+1, а кількість NUL — кількість покажчиків у envp[].
env_bytes=$(env -0 | wc -c)
env_vars=$(env -0 | tr -cd '\0' | wc -c)
budget=$(( arg_max - env_bytes - env_vars * ptr - reserve ))

printf '\n== бюджет аргументів ==\n'
printf '  environ: %s змінних, %s байтів рядків, %s байтів покажчиків\n' \
    "$env_vars" "$env_bytes" "$((env_vars * ptr))"
printf '  бюджет = %s - %s - %s - %s = %s байтів\n' \
    "$arg_max" "$env_bytes" "$((env_vars * ptr))" "$reserve" "$budget"
(( budget > 0 )) || die "бюджет вийшов недодатним: оточення з'їло весь ARG_MAX"

# --- 3. Передбачення -------------------------------------------------------
list="$SELF_TMPDIR/list"
find_err="$SELF_TMPDIR/find.err"
find_rc=0
find "$root" -xdev -ignore_readdir_race -type f -print0 \
    >"$list" 2>"$find_err" || find_rc=$?
if (( find_rc != 0 )); then
    warn "find повернув $find_rc: частина дерева недоступна ($(wc -l <"$find_err") повідомлень)"
fi

cmd=/bin/true   # сама команда теж лежить в argv[] і теж їсть бюджет

predict() {
    # predict ЛІМІТ < NUL-список → «файлів пакетів задовгих»
    local limit=$1
    local path cost
    local base=$(( ${#cmd} + 1 + ptr ))
    local used=$base
    local packets=1 files=0 toolong=0
    while IFS= read -r -d '' path; do
        files=$((files + 1))
        # Ціна одного токена: сам рядок із NUL плюс покажчик у масиві argv[].
        cost=$(( ${#path} + 1 + ptr ))
        if (( ${#path} + 1 > max_arg_strlen )); then
            toolong=$((toolong + 1))
        fi
        if (( used + cost > limit )); then
            packets=$((packets + 1))
            used=$base
        fi
        used=$((used + cost))
    done
    if (( files == 0 )); then packets=0; fi
    printf '%s %s %s\n' "$files" "$packets" "$toolong"
}

read -r files packets toolong < <(predict "$budget" <"$list")
printf '\n== передбачення ==\n'
printf '  файлів у списку: %s\n' "$files"
printf '  пакетів при бюджеті %s: %s\n' "$budget" "$packets"
if (( toolong > 0 )); then
    warn "шляхів довших за MAX_ARG_STRLEN: $toolong — вони дадуть E2BIG у будь-якому разі"
fi
(( files > 0 )) || die "у дереві немає звичайних файлів — нема що міряти"

# --- 4. Що робить справжній xargs -----------------------------------------
# Кожен запуск друкує кількість отриманих аргументів: рядків у виводі —
# стільки, скільки було викликів execve().
run_xargs() {
    local runs_file="$SELF_TMPDIR/runs"
    local rc=0
    xargs -0 -a "$list" -r "$@" -- sh -c 'printf "%s\n" "$#"' _ \
        >"$runs_file" 2>>"$SELF_TMPDIR/xargs.err" || rc=$?
    explain_xargs_status "$rc" || true
    awk '{runs++; args += $1} END {printf "%d %d\n", runs + 0, args + 0}' "$runs_file"
}

printf '\n== фактична робота xargs ==\n'
read -r runs_default args_default < <(run_xargs)
printf '  без -s: %s запусків, %s аргументів\n' "$runs_default" "$args_default"

# GNU xargs добровільно обмежує свій буфер 128 КіБ, навіть коли ядро дозволяє
# більше, — саме тому «без -s» пакетів зазвичай помітно більше за передбачені.
show=$(xargs --show-limits </dev/null 2>&1 || true)
usable=$(printf '%s\n' "$show" \
    | sed -n 's/.*actually use: *\([0-9][0-9]*\).*/\1/p' | tail -n 1)
if [[ -n ${usable:-} ]]; then
    printf '  xargs повідомляє про доступний буфер: %s байтів\n' "$usable"
fi

test_s=$budget
if [[ -n ${usable:-} ]] && (( usable < test_s )); then
    test_s=$usable
    warn "бюджет $budget більший за дозволений xargs — міряємо на $test_s"
fi
read -r runs_sized args_sized < <(run_xargs -s "$test_s")
printf '  з -s %s: %s запусків, %s аргументів\n' "$test_s" "$runs_sized" "$args_sized"

read -r _ packets_sized _ < <(predict "$test_s" <"$list")
printf '  передбачено для того самого -s: %s запусків\n' "$packets_sized"
if (( packets_sized == runs_sized )); then
    printf '  збіг: формула бюджету описує поведінку xargs точно\n'
else
    printf '  розбіжність %s запусків: xargs тримає власний запас під argv[0] і оточення\n' \
        "$(( packets_sized > runs_sized ? packets_sized - runs_sized : runs_sized - packets_sized ))"
fi

# --- 5. Межа одного аргументу ---------------------------------------------
printf '\n== межа MAX_ARG_STRLEN ==\n'
big=$(head -c "$((max_arg_strlen + 1))" /dev/zero | tr '\0' 'a')
if /bin/echo "$big" >/dev/null 2>&1; then
    warn "аргумент $((max_arg_strlen + 1)) байтів пройшов — ядро поводиться інакше, ніж описано"
else
    printf '  один аргумент %s байтів: execve() = E2BIG, як і мало бути\n' \
        "$((max_arg_strlen + 1))"
fi
small=$(head -c "$((max_arg_strlen - 1))" /dev/zero | tr '\0' 'a')
if /bin/echo "$small" >/dev/null 2>&1; then
    printf '  один аргумент %s байтів: пройшов, хоч сумарно це %s КіБ\n' \
        "$((max_arg_strlen - 1))" "$(( (max_arg_strlen - 1) / 1024 ))"
else
    warn "аргумент трохи менший за MAX_ARG_STRLEN не пройшов — перевір ARG_MAX"
fi
printf '  (обидва рядки — локальні змінні оболонки, вони не експортовані\n'
printf '   й тому не з'\''їдають бюджет envp[])\n'
