#!/usr/bin/env bash
# Звіт про фактичне споживання ресурсів юнітом у cgroups v2 — і, головне, про
# те, чи ліміти вже спрацьовували: лічильники memory.events та тротлінг у
# cpu.stat. Живе споглядання дає systemd-cgtop, тут — знімок для журналу.
# Виклик: cgroup-report.sh [--user] [--tree] [юніт]   (типово cron.service)
# Коди: 0 — спокійно, 1 — групи немає, 2 — помилка виклику, 3 — ліміти били.
set -u

CGROUP_ROOT="/sys/fs/cgroup"
UNIT=""
USER_SCOPE=0
SHOW_TREE=0

usage() {
    cat <<'EOF'
Використання: cgroup-report.sh [--user] [--tree] [юніт]
  --user   шукати юніт у менеджері поточного користувача (systemctl --user)
  --tree   додати дерево процесів зрізу (systemd-cgls)
Типовий юніт — cron.service; суфікс .service дописується автоматично.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --user) USER_SCOPE=1 ;;
        --tree) SHOW_TREE=1 ;;
        -h|--help) usage; exit 0 ;;
        --) shift; break ;;
        -*)
            echo "Невідома опція: $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -n "$UNIT" ]; then
                echo "Помилка: юніт указують один раз" >&2
                exit 2
            fi
            UNIT="$1"
            ;;
    esac
    shift
done

[ -n "$UNIT" ] || UNIT="cron.service"
case "$UNIT" in
    *.*) ;;
    *) UNIT="${UNIT}.service" ;;
esac

# Гібридна ієрархія (v1) інтерфейсних файлів нижче просто не має — краще
# сказати це прямо, ніж друкувати таблицю з самих «н/д».
if [ ! -e "${CGROUP_ROOT}/cgroup.controllers" ]; then
    echo "Помилка: ${CGROUP_ROOT} не є уніфікованою ієрархією cgroups v2" >&2
    exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
    echo "Помилка: systemctl недоступний — нема в кого спитати шлях групи" >&2
    exit 1
fi

SYSTEMCTL=(systemctl)
if [ "$USER_SCOPE" -eq 1 ]; then
    SYSTEMCTL=(systemctl --user)
fi

REL=$("${SYSTEMCTL[@]}" show -p ControlGroup --value -- "$UNIT" 2>/dev/null)
if [ -z "$REL" ]; then
    echo "Помилка: юніт «$UNIT» невідомий або не запущений — власної групи немає" >&2
    exit 1
fi

DIR="${CGROUP_ROOT}${REL}"
if [ ! -d "$DIR" ]; then
    echo "Помилка: каталог групи $DIR не існує" >&2
    exit 1
fi

# Значення ключа з файлу «ключ значення»; немає файлу чи ключа — нуль.
kv() {
    if [ ! -r "$1" ]; then
        printf '0'
        return
    fi
    awk -v key="$2" '$1 == key { print $2; hit = 1 } END { if (!hit) print 0 }' "$1"
}

# Однорядковий інтерфейсний файл; облік вимкнено — файлу може не бути зовсім.
one() {
    if [ -r "$1" ]; then
        tr -d '\n' < "$1"
    else
        printf 'н/д'
    fi
}

# Байти у зручні одиниці; «max» і «н/д» лишаються словами.
human() {
    awk -v value="$1" 'BEGIN {
        if (value !~ /^[0-9]+$/) { print value; exit }
        split("Б КіБ МіБ ГіБ ТіБ", unit, " ")
        i = 1
        while (value >= 1024 && i < 5) { value /= 1024; i++ }
        if (i == 1) { printf "%d %s\n", value, unit[i] }
        else { printf "%.1f %s\n", value, unit[i] }
    }'
}

# Лічильники приходять текстом; усе, що не число, зводимо до нуля, аби
# арифметика нижче не спіткнулася на порожньому файлі.
number() {
    case "$1" in
        ''|*[!0-9]*) printf '0' ;;
        *) printf '%s' "$1" ;;
    esac
}

printf "Юніт:             %s\n" "$UNIT"
printf "Контрольна група: %s\n" "$REL"

printf "\n--- Пам'ять ---\n"
printf "  memory.current:  %s\n" "$(human "$(one "$DIR/memory.current")")"
printf "  memory.high:     %s\n" "$(human "$(one "$DIR/memory.high")")"
printf "  memory.max:      %s\n" "$(human "$(one "$DIR/memory.max")")"
printf "  memory.swap.max: %s\n" "$(human "$(one "$DIR/memory.swap.max")")"

EV_HIGH=$(number "$(kv "$DIR/memory.events" high)")
EV_MAX=$(number "$(kv "$DIR/memory.events" max)")
EV_OOM=$(number "$(kv "$DIR/memory.events" oom)")
EV_OOM_KILL=$(number "$(kv "$DIR/memory.events" oom_kill)")
printf "  memory.events:   high=%s max=%s oom=%s oom_kill=%s\n" \
    "$EV_HIGH" "$EV_MAX" "$EV_OOM" "$EV_OOM_KILL"

printf "\n--- Процесор ---\n"
printf "  cpu.max:         %s\n" "$(one "$DIR/cpu.max")"
printf "  cpu.weight:      %s\n" "$(one "$DIR/cpu.weight")"

USAGE_USEC=$(number "$(kv "$DIR/cpu.stat" usage_usec)")
NR_PERIODS=$(number "$(kv "$DIR/cpu.stat" nr_periods)")
NR_THROTTLED=$(number "$(kv "$DIR/cpu.stat" nr_throttled)")
THROTTLED_USEC=$(number "$(kv "$DIR/cpu.stat" throttled_usec)")
printf "  cpu.stat:        usage=%s с, періодів=%s, тротлінгів=%s, простій=%s с\n" \
    "$(awk -v v="$USAGE_USEC" 'BEGIN { printf "%.1f", v / 1000000 }')" \
    "$NR_PERIODS" "$NR_THROTTLED" \
    "$(awk -v v="$THROTTLED_USEC" 'BEGIN { printf "%.1f", v / 1000000 }')"

printf "\n--- Процеси й диск ---\n"
printf "  pids.current:    %s\n" "$(one "$DIR/pids.current")"
printf "  pids.max:        %s\n" "$(one "$DIR/pids.max")"
if [ -r "$DIR/io.stat" ]; then
    printf "  io.stat:\n"
    sed 's/^/    /' "$DIR/io.stat"
else
    printf "  io.stat:         н/д (облік вводу-виводу вимкнено)\n"
fi

PROBLEM=0
printf "\n--- Висновок ---\n"
if [ "$EV_OOM_KILL" -gt 0 ]; then
    printf "  ✖ %s процесів убито ядром за MemoryMax= — завдання не дорахувалося\n" "$EV_OOM_KILL"
    PROBLEM=1
fi
if [ "$NR_THROTTLED" -gt 0 ]; then
    printf "  ✖ квоту CPUQuota= вичерпано %s разів, сумарний простій %s с\n" \
        "$NR_THROTTLED" \
        "$(awk -v v="$THROTTLED_USEC" 'BEGIN { printf "%.1f", v / 1000000 }')"
    PROBLEM=1
fi
if [ "$EV_HIGH" -gt 0 ] && [ "$PROBLEM" -eq 0 ]; then
    # memory.high не вбиває, а гальмує — це попередження, а не аварія.
    printf "  ~ MemoryHigh= спрацьовував %s разів: завдання сповільнювали\n" "$EV_HIGH"
fi
if [ "$PROBLEM" -eq 0 ] && [ "$EV_HIGH" -eq 0 ]; then
    printf "  ✔ жоден ліміт групи не спрацьовував\n"
fi

if [ "$SHOW_TREE" -eq 1 ]; then
    printf "\n--- Дерево процесів ---\n"
    if command -v systemd-cgls >/dev/null 2>&1; then
        systemd-cgls --no-pager "$REL" || true
    else
        echo "  systemd-cgls недоступний" >&2
    fi
fi

if [ "$PROBLEM" -eq 1 ]; then
    exit 3
fi
exit 0
