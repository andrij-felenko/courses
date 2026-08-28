generate_csv_data() {
    (
        # Локаль LC_ALL=C гарантує використання крапки як десяткового роздільника
        export LC_ALL=C
        # Встановлюємо жорстке обмеження віртуальної пам'яті 512MB
        ulimit -v 524288
        # Встановлюємо сувору маску створення файлів
        umask 077
        
        python3 process_financial_records.py > /tmp/export.csv
    )
}
