// Проміжний етап рефакторингу: C ABI залишається сумісним, але лінтер контролює витоки
struct MigratedTelemetryRecord {
    uint16_t               sensor_id;
    uint32_t               timestamp;
    gsl::owner<double*>    readings;      // Лінтер вимагає явного delete[]
    int                    reading_count;
};

// Функція повертає власницький покажчик, закриваючи попередження C26400
gsl::owner<MigratedTelemetryRecord*> allocate_record(int count) {
    auto* rec = new MigratedTelemetryRecord();
    rec->reading_count = count;
    rec->readings = (count > 0) ? new double[count] : nullptr;
    return rec;
}

// Вивільнення з перевіркою правила C26401
void free_record(gsl::owner<MigratedTelemetryRecord*> rec) {
    if (rec) {
        delete[] rec->readings;
        delete rec;
    }
}
