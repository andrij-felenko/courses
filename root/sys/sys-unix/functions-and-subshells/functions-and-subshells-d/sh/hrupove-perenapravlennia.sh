generate_report() {
    {
        printf "=== SYSTEM STATUS REPORT ===\n"
        printf "Generated: %s\n" "$(date)"
        printf "Disk Usage:\n"
        df -h /
        printf "Memory Usage:\n"
        free -m
    } > /var/log/system_report.log 2>&1
}
