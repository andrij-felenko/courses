#!/usr/bin/env bash
# Керування таймер-юнітами systemd: черга, стан, наступні спрацьовування,
# відлік, автозавантаження й позачерговий запуск служби.
# Виклик: timer-control.sh [--user] <команда> [таймер]
#   list      — уся черга таймерів (systemctl list-timers --all)
#   status    — стан таймера і його служби
#   next      — найближчі спрацьовування за виразами OnCalendar=
#   start     — почати відлік у поточній сесії
#   stop      — спинити відлік
#   enable    — до автозавантаження (симлінк у timers.target.wants/)
#   disable   — прибрати з автозавантаження
#   trigger   — запустити службу зараз, не чекаючи розкладу
set -u

USER_SCOPE=0
COMMAND=""
TIMER=""

usage() {
    cat <<'EOF'
Використання: timer-control.sh [--user] <команда> [таймер]
Команди: list | status | next | start | stop | enable | disable | trigger
  --user   працювати з таймерами поточного користувача (systemctl --user)
Суфікс .timer дописується автоматично.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --user) USER_SCOPE=1 ;;
        -h|--help) usage; exit 0 ;;
        -*)
            echo "Невідома опція: $1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -z "$COMMAND" ]; then
                COMMAND="$1"
            elif [ -z "$TIMER" ]; then
                TIMER="$1"
            else
                echo "Помилка: зайвий аргумент «$1»" >&2
                exit 2
            fi
            ;;
    esac
    shift
done

if [ -z "$COMMAND" ]; then
    usage >&2
    exit 2
fi

if ! command -v systemctl >/dev/null 2>&1; then
    echo "Помилка: systemctl недоступний — систему запущено не під systemd" >&2
    exit 1
fi

SYSTEMCTL=(systemctl)
if [ "$USER_SCOPE" -eq 1 ]; then
    SYSTEMCTL=(systemctl --user)
fi

need_timer() {
    if [ -z "$TIMER" ]; then
        echo "Помилка: команда «$COMMAND» вимагає імені таймера" >&2
        exit 2
    fi
    case "$TIMER" in
        *.timer) ;;
        *.*)
            echo "Помилка: «$TIMER» — не таймер-юніт" >&2
            exit 2
            ;;
        *) TIMER="${TIMER}.timer" ;;
    esac
    # Юніта може не бути зовсім — тоді systemctl start мовчки створив би
    # завдання на неіснуючий юніт і впав лише в журналі.
    if ! "${SYSTEMCTL[@]}" cat -- "$TIMER" >/dev/null 2>&1; then
        echo "Помилка: юніт «$TIMER» не знайдено" >&2
        exit 1
    fi
}

# Службу таймер називає сам: Unit= у [Timer] або однойменний .service.
activated_service() {
    local unit
    unit=$("${SYSTEMCTL[@]}" show -p Unit --value -- "$TIMER" 2>/dev/null)
    if [ -z "$unit" ]; then
        unit="${TIMER%.timer}.service"
    fi
    printf '%s' "$unit"
}

case "$COMMAND" in
    list)
        if [ -n "$TIMER" ]; then
            "${SYSTEMCTL[@]}" list-timers --all --no-pager -- "$TIMER"
        else
            "${SYSTEMCTL[@]}" list-timers --all --no-pager
        fi
        ;;

    status)
        need_timer
        SERVICE=$(activated_service)
        # status повертає 3 для неактивного юніта — це стан, а не помилка,
        # тож код повернення сюди не пропускаємо.
        "${SYSTEMCTL[@]}" status --no-pager -- "$TIMER" || true
        printf "\n--- Служба, яку активує таймер ---\n"
        "${SYSTEMCTL[@]}" status --no-pager -- "$SERVICE" || true
        ;;

    next)
        need_timer
        CALENDARS=$("${SYSTEMCTL[@]}" cat -- "$TIMER" 2>/dev/null |
            sed -n 's/^[[:space:]]*OnCalendar=[[:space:]]*//p')
        if [ -z "$CALENDARS" ]; then
            echo "Таймер монотонний: OnCalendar= немає, розклад рахується від подій."
            "${SYSTEMCTL[@]}" show \
                -p TimersMonotonic -p NextElapseUSecMonotonic -- "$TIMER"
            exit 0
        fi
        if ! command -v systemd-analyze >/dev/null 2>&1; then
            echo "systemd-analyze недоступний, показую самі вирази:" >&2
            printf '%s\n' "$CALENDARS"
            exit 0
        fi
        printf '%s\n' "$CALENDARS" | while IFS= read -r EXPR; do
            [ -n "$EXPR" ] || continue
            printf "OnCalendar=%s\n" "$EXPR"
            systemd-analyze calendar --iterations=3 -- "$EXPR" | sed 's/^/  /'
        done
        ;;

    start|stop)
        need_timer
        if "${SYSTEMCTL[@]}" "$COMMAND" -- "$TIMER"; then
            "${SYSTEMCTL[@]}" list-timers --all --no-pager -- "$TIMER"
        else
            echo "Помилка: не вдалося виконати «$COMMAND» для $TIMER" >&2
            exit 1
        fi
        ;;

    enable|disable)
        need_timer
        if ! "${SYSTEMCTL[@]}" "$COMMAND" -- "$TIMER"; then
            if [ "$USER_SCOPE" -eq 0 ] && [ "$(id -u)" -ne 0 ]; then
                echo "Підказка: системні юніти вмикає root (спробуйте sudo)" >&2
            fi
            exit 1
        fi
        ;;

    trigger)
        need_timer
        SERVICE=$(activated_service)
        # Запуск служби руками не зсуває розкладу: таймер лишається
        # active (waiting) і відлічує свою наступну точку.
        echo "Запускаю $SERVICE позачергово; розклад $TIMER не змінюється."
        if ! "${SYSTEMCTL[@]}" start -- "$SERVICE"; then
            echo "Помилка: службу $SERVICE не запущено" >&2
            exit 1
        fi
        "${SYSTEMCTL[@]}" status --no-pager -- "$SERVICE" || true
        ;;

    *)
        echo "Невідома команда: $COMMAND" >&2
        usage >&2
        exit 2
        ;;
esac
