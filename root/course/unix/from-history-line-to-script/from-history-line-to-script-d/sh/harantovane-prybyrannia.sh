declare -a BACKGROUND_PIDS=()

cleanup() {
    local exit_code=$?
    # Вимикаємо пастку для запобігання рекурсивним викликам
    trap - EXIT INT TERM HUP

    # Завершення фонових воркерів, щоб вони не перетворилися на зомбі
    if [[ ${#BACKGROUND_PIDS[@]} -gt 0 ]]; then
        kill -TERM "${BACKGROUND_PIDS[@]}" 2>/dev/null || true
        wait "${BACKGROUND_PIDS[@]}" 2>/dev/null || true
    fi

    if [[ -d "${TMP_DIR:-}" ]]; then
        rm -rf "${TMP_DIR}"
    fi

    exit "${exit_code}"
}

# Реєстрація єдиної точки виходу
trap cleanup EXIT INT TERM HUP
