# Дефектний код:
fetch_metrics() {
    local metrics_data=$(curl -sSf "https://metrics.service.internal/api")
    echo "Дані отримано: ${metrics_data}"
}

# Безпечний еквівалент:
fetch_metrics() {
    local metrics_data
    metrics_data=$(curl -sSf "https://metrics.service.internal/api")
    echo "Дані отримано: ${metrics_data}"
}
