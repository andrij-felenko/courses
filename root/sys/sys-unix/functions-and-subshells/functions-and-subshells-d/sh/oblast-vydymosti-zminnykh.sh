process_files() {
    for i in /tmp/*.dat; do
        format_file "$i"
    done
}

format_file() {
    # Помилка: 'i' не оголошено локальною!
    for i in 1 2 3; do
        printf "."
    done
}
