#!/usr/bin/env bash
# Діагностика періодичного завдання за журналом systemd-journald: на відміну
# від cron, вивід нікуди не поділося — він структурований і фільтрується.
# Виклик: timer-logs.sh [--user] <команда> <юніт> [аргументи]
#   service          — увесь журнал виконання служби
#   timer            — події планування самого таймера
#   last             — лише останній запуск (за _SYSTEMD_INVOCATION_ID)
#   boot             — записи поточного сеансу завантаження
#   errors           — лише пріоритети err..emerg
#   range <від> <до> — точний проміжок (--since / --until)
#   follow           — стеження в реальному часі, short-precise
#   json [N]         — останні N записів (типово 50) у json-pretty
set -u

USER_SCOPE=0
COMMAND=""
UNIT=""
ARGS=()

usage() {
    cat <<'EOF'
Використання: timer-logs.sh [--user] <команда> <юніт> [аргументи]
Команди: service | timer | last | boot | errors | range <від> <до> | follow | json [N]
  --user   читати журнал поточного користувача (journalctl --user)
Приклад: timer-logs.sh range backup "2026-08-29 02:00:00" "2026-08-29 04:00:00"
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
            elif [ -z "$UNIT" ]; then
                UNIT="$1"
            else
                ARGS+=("$1")
            fi
            ;;
    esac
    shift
done

if [ -z "$COMMAND" ] || [ -z "$UNIT" ]; then
    usage >&2
    exit 2
fi

if ! command -v journalctl >/dev/null 2>&1; then
    echo "Помилка: journalctl недоступний" >&2
    exit 1
fi

# Ім'я доповнюємо за командою: «timer» дивиться на таймер-юніт, решта — на
# службу, бо саме вона друкує stdout і stderr завдання.
case "$UNIT" in
    *.service|*.timer) ;;
    *.*)
        echo "Помилка: «$UNIT» не схожий на юніт служби чи таймера" >&2
        exit 2
        ;;
    *)
        if [ "$COMMAND" = "timer" ]; then
            UNIT="${UNIT}.timer"
        else
            UNIT="${UNIT}.service"
        fi
        ;;
esac

JOURNAL=(journalctl --no-pager)
UNIT_FLAG="-u"
SYSTEMCTL=(systemctl)
if [ "$USER_SCOPE" -eq 1 ]; then
    JOURNAL=(journalctl --no-pager --user)
    UNIT_FLAG="--user-unit"
    SYSTEMCTL=(systemctl --user)
fi

case "$COMMAND" in
    service|timer)
        "${JOURNAL[@]}" "$UNIT_FLAG" "$UNIT"
        ;;

    last)
        # InvocationID унікальний для КОЖНОГО спрацьовування таймера: за ним
        # видно рівно останній запуск, без сусідніх діб у тому самому юніті.
        INVOCATION=$("${SYSTEMCTL[@]}" show -p InvocationID --value -- "$UNIT" 2>/dev/null)
        if [ -z "$INVOCATION" ]; then
            echo "Юніт «$UNIT» ще жодного разу не запускався в цьому сеансі" >&2
            exit 1
        fi
        "${JOURNAL[@]}" _SYSTEMD_INVOCATION_ID="$INVOCATION"
        ;;

    boot)
        "${JOURNAL[@]}" "$UNIT_FLAG" "$UNIT" -b
        ;;

    errors)
        "${JOURNAL[@]}" "$UNIT_FLAG" "$UNIT" -p err..emerg
        ;;

    range)
        if [ "${#ARGS[@]}" -lt 2 ]; then
            echo "Помилка: range вимагає двох міток часу — від і до" >&2
            usage >&2
            exit 2
        fi
        "${JOURNAL[@]}" "$UNIT_FLAG" "$UNIT" --since "${ARGS[0]}" --until "${ARGS[1]}"
        ;;

    follow)
        # short-precise додає мікросекунди, за якими видно справжній розкид
        # спрацьовувань довкола вікна AccuracySec=.
        "${JOURNAL[@]}" "$UNIT_FLAG" "$UNIT" -f -o short-precise
        ;;

    json)
        LINES="${ARGS[0]:-50}"
        case "$LINES" in
            ''|*[!0-9]*)
                echo "Помилка: кількість записів «$LINES» має бути числом" >&2
                exit 2
                ;;
        esac
        "${JOURNAL[@]}" "$UNIT_FLAG" "$UNIT" -n "$LINES" -o json-pretty
        ;;

    *)
        echo "Невідома команда: $COMMAND" >&2
        usage >&2
        exit 2
        ;;
esac
