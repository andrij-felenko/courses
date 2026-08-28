process_records() {
    local record_id="$1"
    
    # Трасуємо лише специфічний проблемний запис
    if [[ "${record_id}" -eq 404 ]]; then
        set -x
    fi

    perform_complex_calculation "${record_id}"

    if [[ "${record_id}" -eq 404 ]]; then
        set +x
    fi
}
