// Єдина точка правди про формат дати
std::string fmtDate(const Date& d) {
    char buf[16];
    std::snprintf(buf, sizeof buf, "%02d.%02d.%04d", d.day, d.month, d.year);
    return buf;
}

// Клієнти знають лише виклик, не формат
std::string report  = fmtDate(d);   // звіт
std::string expLine = fmtDate(d);   // експорт
std::string ui      = fmtDate(d);   // UI
