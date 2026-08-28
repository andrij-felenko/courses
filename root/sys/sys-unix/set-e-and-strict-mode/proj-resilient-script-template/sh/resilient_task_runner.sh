#!/usr/bin/env bash
# ==============================================================================
# НАЗВА: resilient_task_runner.sh
# ОПИС:  Виробничий шаблон сценарію з повною підтримкою Strict Mode,
#        стековим трасуванням помилок та автоматичним очищенням ресурсів.
# ==============================================================================

# 1. Активація захисного режиму виконання
set -euo pipefail
set -E                               # Успадкування trap ERR у функціях та підоболонках
shopt -s inherit_errexit 2>/dev/null || true  # Успадкування set -e у $(...) (Bash 4.4+)

# 2. Оголошення глобальних констант середовища
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

# Глобальна змінна для відстеження тимчасового робочого каталогу
WORK_DIR=""

# 3. Функції форматованого логування в stderr (не ламають потік stdout)
log_info() {
    printf "[%s] [INFO]  %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

log_warn() {
    printf "[%s] [WARN]  %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

log_error() {
    printf "[%s] [ERROR] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

# 4. Обробник аварійного стану та реконструкція стека викликів
handle_error() {
    local exit_code="$1"
    local line_no="$2"
    local failed_cmd="${BASH_COMMAND:-unknown}"

    log_error "=========================================================="
    log_error "АВАРІЙНА ЗУПИНКА СЦЕНАРІЮ"
    log_error "Команда: '${failed_cmd}'"
    log_error "Статус помилки: ${exit_code}"
    log_error "Місце збою: файл ${BASH_SOURCE[1]:-${SCRIPT_NAME}}, рядок ${line_no}"
    log_error "----------------------------------------------------------"
    log_error "Стек викликів (Call Stack Backtrace):"

    local frame=0
    while caller "${frame}" >/dev/null 2>&1; do
        local frame_info
        frame_info="$(caller "${frame}")"
        local c_line c_func c_file
        read -r c_line c_func c_file <<< "${frame_info}"
        log_error "  [${frame}] ${c_file}:${c_line} -> ${c_func}()"
        (( frame++ ))
    done
    log_error "=========================================================="
}

# 5. Гарантоване очищення тимчасових ресурсів (Idempotent Cleanup)
cleanup() {
    local exit_status=$?
    # Тимчасово вимикаємо errexit, щоб помилки при видаленні файлів не блокували вихід
    set +e

    if [[ -n "${WORK_DIR:-}" && -d "${WORK_DIR}" ]]; then
        log_info "Видалення тимчасового каталогу: ${WORK_DIR}"
        rm -rf "${WORK_DIR}"
    fi

    if [[ ${exit_status} -eq 0 ]]; then
        log_info "Сценарій успішно завершив роботу."
    else
        log_warn "Сценарій завершився з аварійним кодом: ${exit_status}"
    fi

    exit "${exit_status}"
}

# 6. Реєстрація системних пасток
trap 'handle_error $? $LINENO' ERR
trap cleanup EXIT
trap 'log_warn "Отримано сигнал SIGINT (Ctrl+C). Зупинка..."; exit 130' INT
trap 'log_warn "Отримано сигнал SIGTERM. Завершення процесу..."; exit 143' TERM

# 7. Допоміжні функції безпечного виконання

# Виконання команди, падіння якої є очікуваним і не повинно переривати скрипт
run_optional() {
    local status=0
    "$@" || status=$?
    return "${status}"
}

# 8. Розбір та валідація аргументів командного рядка
print_usage() {
    cat <<EOF
Використання: ${SCRIPT_NAME} [ОПЦІЇ]

Опції:
  -t, --target DIR     Цільовий каталог для обробки (обов'язковий)
  -b, --batch-size N   Розмір пакетної обробки (за замовчуванням: 50)
  -v, --verbose        Увімкнути детальний режим (set -x)
  -h, --help           Показати цю довідку та вийти
EOF
}

parse_arguments() {
    TARGET_DIR=""
    BATCH_SIZE=50
    VERBOSE=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -t|--target)
                [[ $# -ge 2 ]] || { log_error "Опція '$1' вимагає аргументу"; exit 1; }
                TARGET_DIR="$2"
                shift 2
                ;;
            -b|--batch-size)
                [[ $# -ge 2 ]] || { log_error "Опція '$1' вимагає аргументу"; exit 1; }
                BATCH_SIZE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                log_error "Невідомий параметр: $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # Валідація обов'язкових параметрів
    if [[ -z "${TARGET_DIR}" ]]; then
        log_error "Помилка: параметр --target є обов'язковим."
        print_usage
        exit 1
    fi

    # Валідація числового формату batch-size
    if ! [[ "${BATCH_SIZE}" =~ ^[1-9][0-9]*$ ]]; then
        log_error "Помилка: --batch-size має бути додатним цілим числом (отримано: '${BATCH_SIZE}')."
        exit 1
    fi

    if [[ ${VERBOSE} -eq 1 ]]; then
        log_info "Активація режиму динамічного трасування xtrace (set -x)"
        set -x
    fi
}

# 9. Бізнес-логіка сценарію
process_data_payload() {
    local source_dir="$1"
    local batch_limit="$2"

    log_info "Створення ізольованого робочого середовища..."
    WORK_DIR="$(mktemp -d "/tmp/task_runner_XXXXXX")"
    log_info "Робочий каталог створено: ${WORK_DIR}"

    local staging_file="${WORK_DIR}/staging.data"
    local output_archive="${WORK_DIR}/result.tar.gz"

    log_info "Генерація тестових даних у ${staging_file}..."
    printf "record_%04d,value_%d\n" {1..100} 42 > "${staging_file}"

    log_info "Виконання фільтрації через конвеєр із перевіркою pipefail..."
    # Конвеєр безпечно контролюється set -o pipefail
    grep "record_" "${staging_file}" \
        | head -n "${batch_limit}" \
        | gzip -c > "${output_archive}"

    # Безпечне читання статусу останньої операції
    log_info "Розмір згенерованого архіву: $(wc -c < "${output_archive}") байтів"

    log_info "Перевірка обробки помилок, що не є фатальними..."
    if run_optional grep -q "non_existent_key" "${staging_file}"; then
        log_info "Ключ знайдено."
    else
        log_info "Очікувано: ключ не знайдено, статус 1 безпечно оброблено без зупинки скрипту."
    fi
}

# 10. Точка входу в програму (Main Entry Point)
main() {
    log_info "Ініціалізація сценарію '${SCRIPT_NAME}'..."
    parse_arguments "$@"

    log_info "Початок обробки для цілі: '${TARGET_DIR}', розмір пакета: ${BATCH_SIZE}"
    process_data_payload "${TARGET_DIR}" "${BATCH_SIZE}"
    log_info "Усі операції успішно завершено."
}

# Запуск головної функції з передачею всіх параметрів
main "$@"
