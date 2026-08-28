# POSIX-сумісна форма (рекомендована для всіх переносних скриптів)
cleanup_temp() {
    rm -f /tmp/app_*.tmp
}

# POSIX-форма з перенаправленням на рівні всього тіла функції
log_event() {
    printf "[%s] %s\n" "$(date +%T)" "$*"
} >> /var/log/app.log 2>&1

# Форма KornShell / Bash з ключовим словом function
function backup_data {
    tar -czf /backup/data.tar.gz /var/data
}
