# Стандартна POSIX-форма
calculate_total() {
    local_sum=$(( $1 + $2 ))
    echo "$local_sum"
}

# Допустима форма: тіло функції як підоболонка в круглих дужках
isolated_work() (
    cd /tmp || exit 1
    rm -f *.cache
)

# Функція з постійним перенаправленням потоку виводу
log_notice() {
    printf "[%s] %s\n" "$(date +%T)" "$*"
} >> /var/log/service.log 2>&1
