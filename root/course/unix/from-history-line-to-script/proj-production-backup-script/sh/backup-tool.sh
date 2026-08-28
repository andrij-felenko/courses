#!/usr/bin/env bash
# ==============================================================================
# backup-tool.sh — Надійний сценарій резервного копіювання каталогів
# ==============================================================================

# 1. Активація суворого режиму виконання
set -euo pipefail
IFS=$'\n\t'

# 2. Налаштування розширеного трасування для діагностики
export PS4='+ ${BASH_SOURCE[0]}:${LINENO}:${FUNCNAME[0]:+${FUNCNAME[0]}(): } '

# 3. Константи та змінні конфігурації за замовчуванням
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOCK_FILE="/tmp/${SCRIPT_NAME}.lock"

SOURCE_DIR=""
DEST_DIR=""
RETENTION_DAYS=7
VERBOSE=0

# 4. Функції форматованого логування у потік stderr
log_timestamp() {
    date +'%Y-%m-%dT%H:%M:%S%z'
}

log_info() {
    printf '[%s] [INFO]  %s\n' "$(log_timestamp)" "$*" >&2
}

log_warn() {
    printf '[%s] [WARN]  %s\n' "$(log_timestamp)" "$*" >&2
}

log_error() {
    printf '[%s] [ERROR] %s\n' "$(log_timestamp)" "$*" >&2
}

log_fatal() {
    printf '[%s] [FATAL] %s\n' "$(log_timestamp)" "$*" >&2
    exit 1
}

# 5. Довідкова інформація
usage() {
    cat <<EOF >&2
Використання: ${SCRIPT_NAME} [ОПЦІЇ] -s <вихідний_каталог> -d <каталог_призначення>

Обов'язкові параметри:
  -s, --source DIR       Каталог, резервну копію якого слід створити
  -d, --dest DIR         Каталог, куди буде збережено фінальний архів

Опції:
  -k, --keep DAYS        Кількість днів зберігання архівів (за замовчуванням: 7)
  -v, --verbose          Увімкнути режим детального виводу (xtrace)
  -h, --help             Показати цю довідку та вийти

Приклад:
  ${SCRIPT_NAME} -s /var/www/my-site -d /var/backups/sites -k 14
EOF
    exit 2
}

# 6. Обробка позиційних аргументів через getopts
parse_arguments() {
    while getopts ":s:d:k:vh-:" opt; do
        # Підтримка довгих опцій через синтаксис --option
        if [[ "${opt}" == "-" ]]; then
            case "${OPTARG}" in
                source)       opt="s"; OPTARG="${!OPTIND}"; OPTIND=$((OPTIND + 1)) ;;
                dest)         opt="d"; OPTARG="${!OPTIND}"; OPTIND=$((OPTIND + 1)) ;;
                keep)         opt="k"; OPTARG="${!OPTIND}"; OPTIND=$((OPTIND + 1)) ;;
                verbose)      opt="v" ;;
                help)         opt="h" ;;
                *)            log_error "Невідомий параметр --${OPTARG}"; usage ;;
            esac
        fi

        case "${opt}" in
            s) SOURCE_DIR="${OPTARG}" ;;
            d) DEST_DIR="${OPTARG}" ;;
            k)
                if [[ ! "${OPTARG}" =~ ^[0-9]+$ ]]; then
                    log_fatal "Значення терміну зберігання має бути додатним числом: ${OPTARG}"
                fi
                RETENTION_DAYS="${OPTARG}"
                ;;
            v) VERBOSE=1 ;;
            h) usage ;;
            \?) log_error "Невідомий прапорець: -${OPTARG}"; usage ;;
            :)  log_error "Опція -${OPTARG} вимагає аргументу."; usage ;;
        esac
    done

    # Валідація обов'язкових параметрів
    if [[ -z "${SOURCE_DIR}" ]] || [[ -z "${DEST_DIR}" ]]; then
        log_error "Помилка: обов'язкові параметри -s та -d не вказані."
        usage
    fi

    # Перевірка наявності вихідного каталогу
    if [[ ! -d "${SOURCE_DIR}" ]]; then
        log_fatal "Вихідний каталог не існує: ${SOURCE_DIR}"
    fi

    # Перетворення шляхів в абсолютні для уникнення проблем із робочим каталогом
    SOURCE_DIR="$(cd "${SOURCE_DIR}" && pwd)"
}

# 7. Ініціалізація блокування файлу через flock для виключного доступу
acquire_lock() {
    # Відкриваємо файловий дескриптор 200 на запис до lock-файлу
    exec 200>"${LOCK_FILE}"
    if ! flock -n 200; then
        log_warn "Інший екземпляр ${SCRIPT_NAME} вже виконується. Завершення роботи."
        exit 0
    fi
}

# 8. Керування тимчасовими ресурсами та реєстрація пасток
setup_sandbox() {
    TMP_DIR="$(mktemp -d -t "${SCRIPT_NAME}.XXXXXX")"
    log_info "Виділено ізольований тимчасовий каталог: ${TMP_DIR}"

    # Реєстрація єдиної точки очищення
    trap cleanup EXIT INT TERM HUP
}

cleanup() {
    local exit_code=$?
    # Вимикаємо пастку, щоб уникнути циклічних викликів
    trap - EXIT INT TERM HUP

    if [[ -n "${TMP_DIR:-}" ]] && [[ -d "${TMP_DIR}" ]]; then
        log_info "Очищення тимчасового каталогу: ${TMP_DIR}"
        rm -rf "${TMP_DIR}"
    fi

    # Закриття файлового дескриптора замка
    exec 200>&- || true

    if [[ ${exit_code} -ne 0 ]]; then
        log_error "Сценарій аварійно завершився з кодом ${exit_code}."
    fi
    exit "${exit_code}"
}

# 9. Основна логіка резервного копіювання
create_backup() {
    local source_name
    source_name="$(basename "${SOURCE_DIR}")"
    local timestamp
    timestamp="$(date +'%Y%m%d_%H%M%S')"
    local archive_filename="${source_name}_${timestamp}.tar.gz"
    local checksum_filename="${archive_filename}.sha256"

    local temp_archive_path="${TMP_DIR}/${archive_filename}"
    local temp_checksum_path="${TMP_DIR}/${checksum_filename}"

    log_info "Початок архівації каталогу '${SOURCE_DIR}'..."

    # Створення стисненого архіву у тимчасовому каталозі
    # Опція -C переходить у батьківський каталог, щоб в архіві не зберігався повний абсолютний шлях
    tar -czf "${temp_archive_path}" -C "$(dirname "${SOURCE_DIR}")" "${source_name}"
    log_info "Архів успішно сформовано: ${temp_archive_path} ($(du -h "${temp_archive_path}" | cut -f1))"

    # Генерація контрольної суми SHA-256
    log_info "Обчислення контрольної суми SHA-256..."
    (
        cd "${TMP_DIR}"
        sha256sum "${archive_filename}" > "${checksum_filename}"
    )

    # Підготовка каталогу призначення
    if [[ ! -d "${DEST_DIR}" ]]; then
        log_info "Каталог призначення не існує. Створення: ${DEST_DIR}"
        mkdir -p "${DEST_DIR}"
    fi
    DEST_DIR="$(cd "${DEST_DIR}" && pwd)"

    # Атомарне переміщення результатів у каталог призначення
    log_info "Атомарна фіксація архіву в цільовому сховищі: ${DEST_DIR}"
    mv "${temp_archive_path}" "${DEST_DIR}/${archive_filename}"
    mv "${temp_checksum_path}" "${DEST_DIR}/${checksum_filename}"

    log_info "Верифікація збереженого архіву за контрольною сумою..."
    (
        cd "${DEST_DIR}"
        sha256sum --check --status "${checksum_filename}"
    )
    log_info "Перевірку цілісності пройдено успішно."
}

# 10. Ротація застарілих копій
rotate_old_backups() {
    local source_name
    source_name="$(basename "${SOURCE_DIR}")"
    log_info "Перевірка застарілих резервних копій (термін зберігання: ${RETENTION_DAYS} днів)..."

    local deleted_count=0
    while IFS= read -r -d $'\0' old_file; do
        log_info "Видалення застарілого файлу: $(basename "${old_file}")"
        rm -f "${old_file}"
        deleted_count=$((deleted_count + 1))
    done < <(find "${DEST_DIR}" -maxdepth 1 -type f -name "${source_name}_*.tar.gz*" -mtime +"${RETENTION_DAYS}" -print0)

    log_info "Ротацію завершено. Видалено файлів: ${deleted_count}"
}

# 11. Головна точка входу
main() {
    parse_arguments "$@"

    if [[ ${VERBOSE} -eq 1 ]]; then
        set -x
    fi

    log_info "=== Запуск резервного копіювання [PID: $$] ==="
    acquire_lock
    setup_sandbox
    create_backup
    rotate_old_backups
    log_info "=== Резервне копіювання успішно завершено ==="
}

main "$@"
