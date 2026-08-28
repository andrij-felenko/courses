std::vector<std::string> splitLabels(const std::string &s) {
    std::vector<std::string> out;
    for (size_t start = 0;;) {
        const size_t comma = s.find(',', start);
        if (comma == std::string::npos) { out.push_back(s.substr(start)); break; }
        out.push_back(s.substr(start, comma - start));
        start = comma + 1;
    }
    return out;
}

// Рядок формату плюс підписи → таблиця полів зі зміщеннями від початку пакета.
bool buildLayout(const std::string &format, const std::string &labels, Layout &lay) {
    const std::vector<std::string> names = splitLabels(labels);
    size_t off = HDR;
    lay.fields.clear();
    for (size_t k = 0; k < format.size(); ++k) {
        Letter t;
        if (!letterInfo(format[k], t)) return false;   // чужа літера — далі все з'їде
        lay.fields.push_back({ k < names.size() ? names[k] : std::string(),
                               off, format[k], t });
        off += t.size;
    }
    return off == lay.length;      // сума полів мусить збігтися з оголошеною довжиною
}

// Число за зміщенням, зведене до double. memcpy — бо поля в пакеті не вирівняні.
double readNumber(const uint8_t *p, const Letter &t) {
    double raw = 0.0;
    switch (t.kind) {
    case 'i': {
        int64_t v = 0;
        if      (t.size == 1) { int8_t  x; std::memcpy(&x, p, 1); v = x; }
        else if (t.size == 2) { int16_t x; std::memcpy(&x, p, 2); v = x; }
        else if (t.size == 4) { int32_t x; std::memcpy(&x, p, 4); v = x; }
        else                  { int64_t x; std::memcpy(&x, p, 8); v = x; }
        raw = static_cast<double>(v);
        break;
    }
    case 'u': {
        uint64_t v = 0;
        if      (t.size == 1) { uint8_t  x; std::memcpy(&x, p, 1); v = x; }
        else if (t.size == 2) { uint16_t x; std::memcpy(&x, p, 2); v = x; }
        else if (t.size == 4) { uint32_t x; std::memcpy(&x, p, 4); v = x; }
        else                  { uint64_t x; std::memcpy(&x, p, 8); v = x; }
        raw = static_cast<double>(v);
        break;
    }
    case 'f':
        if (t.size == 4) { float  x; std::memcpy(&x, p, 4); raw = x; }
        else             { double x; std::memcpy(&x, p, 8); raw = x; }
        break;
    default:
        return 0.0;                // рядок чи масив числом не буває
    }
    return raw * t.mult;
}

// Рядок у пакеті займає рівно size байтів і нульового байта може не мати.
std::string readText(const uint8_t *p, size_t size) {
    size_t n = 0;
    while (n < size && p[n] != '\0') ++n;
    return std::string(reinterpret_cast<const char *>(p), n);
}

// Єдина розкладка, яку доводиться знати наперед: FMT описує сам себе.
Layout fmtLayout() {
    Layout lay;
    lay.name   = "FMT";
    lay.length = 89;                                   // 3 + 1 + 1 + 4 + 16 + 64
    if (!buildLayout("BBnNZ", "Type,Length,Name,Format,Columns", lay)) std::abort();
    return lay;
}

} // namespace
