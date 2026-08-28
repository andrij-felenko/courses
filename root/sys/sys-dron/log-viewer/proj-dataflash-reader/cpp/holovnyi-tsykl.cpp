int main(int argc, char **argv) {
    if (argc != 3) {
        std::fprintf(stderr, "вжиток: dfcsv <лог.bin> <ATT.Roll | IMU[1].GyrX>\n");
        return 2;
    }
    const std::string spec = argv[2];
    const size_t dot = spec.rfind('.');
    if (dot == std::string::npos || dot + 1 == spec.size()) {
        std::fprintf(stderr, "очікую вигляд ATT.Roll або IMU[1].GyrX\n");
        return 2;
    }
    const std::string wantField = spec.substr(dot + 1);
    std::string wantMsg = spec.substr(0, dot);
    int wantInstance = -1;                        // −1 означає «байдуже»
    const size_t brk = wantMsg.find('[');
    if (brk != std::string::npos) {
        wantInstance = std::atoi(wantMsg.c_str() + brk + 1);
        wantMsg.erase(brk);
    }

    std::ifstream in(argv[1], std::ios::binary);
    if (!in) { std::fprintf(stderr, "не відкривається: %s\n", argv[1]); return 1; }
    std::streambuf *src = in.rdbuf();

    std::map<uint8_t, Layout> layouts;
    layouts[FMT_TYPE] = fmtLayout();

    int      wantType  = -1;                      // з'явиться разом з оголошенням
    size_t   idxValue  = 0, idxTime = 0, idxInst = 0;
    bool     hasTime   = false, hasInst = false;
    double   timeScale = 1e-6;
    uint64_t rows = 0, slides = 0;

    std::vector<uint8_t> pkt;
    uint8_t win[HDR];
    size_t  have = 0;
    bool    running = true;

    while (running) {
        while (have < HDR) {                      // добираємо вікно до трьох байтів
            const int c = src->sbumpc();
            if (c == std::char_traits<char>::eof()) { running = false; break; }
            win[have++] = static_cast<uint8_t>(c);
        }
        if (!running) break;

        const auto it = layouts.find(win[2]);
        if (win[0] != HEAD1 || win[1] != HEAD2 || it == layouts.end()) {
            win[0] = win[1];                      // зсув вікна на один байт
            win[1] = win[2];
            have   = HDR - 1;
            ++slides;
            continue;
        }

        const uint8_t type = win[2];
        const size_t  len  = it->second.length;
        pkt.assign(len, uint8_t{0});
        std::memcpy(pkt.data(), win, HDR);
        for (size_t k = HDR; k < len; ++k) {
            const int c = src->sbumpc();
            if (c == std::char_traits<char>::eof()) { running = false; break; }
            pkt[k] = static_cast<uint8_t>(c);
        }
        if (!running) break;                      // обірваний хвіст файлу
        have = 0;

        if (type == FMT_TYPE) {
            const Layout &f = layouts.at(FMT_TYPE);
            const uint8_t newType = static_cast<uint8_t>(
                readNumber(pkt.data() + f.fields[0].off, f.fields[0].type));
            if (newType == FMT_TYPE) continue;    // FMT про самого себе — уже знаємо

            Layout lay;
            lay.length = static_cast<uint8_t>(
                readNumber(pkt.data() + f.fields[1].off, f.fields[1].type));
            lay.name = readText(pkt.data() + f.fields[2].off, f.fields[2].type.size);
            const std::string format =
                readText(pkt.data() + f.fields[3].off, f.fields[3].type.size);
            const std::string labels =
                readText(pkt.data() + f.fields[4].off, f.fields[4].type.size);

            if (!buildLayout(format, labels, lay)) {
                std::fprintf(stderr, "пропущено %s: «%s» не дає %u байтів\n",
                             lay.name.c_str(), format.c_str(), unsigned(lay.length));
                continue;
            }
            layouts[newType] = lay;

            if (lay.name != wantMsg || wantType >= 0) continue;

            size_t v = SIZE_MAX, tUS = SIZE_MAX, tMS = SIZE_MAX;
            for (size_t k = 0; k < lay.fields.size(); ++k) {
                const std::string &l = lay.fields[k].label;
                if (l == wantField)              v   = k;
                if (l == "TimeUS")               tUS = k;
                if (l == "TimeMS")               tMS = k;
                if (l == "I" || l == "Instance") { idxInst = k; hasInst = true; }
            }
            if (v == SIZE_MAX) {
                std::string all;
                for (const Field &fl : lay.fields) { all += fl.label; all += ' '; }
                std::fprintf(stderr, "у %s немає поля «%s». Є: %s\n",
                             wantMsg.c_str(), wantField.c_str(), all.c_str());
                return 1;
            }
            if (lay.fields[v].type.kind == 's' || lay.fields[v].type.kind == 'x') {
                std::fprintf(stderr, "%s — не число (літера %c)\n",
                             spec.c_str(), lay.fields[v].code);
                return 1;
            }
            if (hasInst && wantInstance < 0)
                std::fprintf(stderr, "увага: %s має поле екземпляра «%s» — у виводі "
                                     "змішано всі; вкажіть %s[0].%s, щоб узяти один\n",
                             wantMsg.c_str(), lay.fields[idxInst].label.c_str(),
                             wantMsg.c_str(), wantField.c_str());

            idxValue = v;
            if      (tUS != SIZE_MAX) { idxTime = tUS; timeScale = 1e-6; hasTime = true; }
            else if (tMS != SIZE_MAX) { idxTime = tMS; timeScale = 1e-3; hasTime = true; }
            wantType = newType;
            std::printf("%s,%s\n", hasTime ? "time_s" : "n", spec.c_str());
            continue;
        }

        if (static_cast<int>(type) != wantType) continue;

        const Layout &lay = layouts.at(type);
        if (hasInst && wantInstance >= 0) {
            const Field &fi = lay.fields[idxInst];
            if (static_cast<int>(readNumber(pkt.data() + fi.off, fi.type)) != wantInstance)
                continue;
        }
        const Field &fv = lay.fields[idxValue];
        const double value = readNumber(pkt.data() + fv.off, fv.type);
        if (hasTime) {
            const Field &ft = lay.fields[idxTime];
            const double t = readNumber(pkt.data() + ft.off, ft.type) * timeScale;
            std::printf("%.6f,%.9g\n", t, value);
        } else {
            std::printf("%llu,%.9g\n", static_cast<unsigned long long>(rows), value);
        }
        ++rows;
    }

    if (wantType < 0) {
        std::fprintf(stderr, "у логу немає оголошення повідомлення %s\n", wantMsg.c_str());
        return 1;
    }
    std::fprintf(stderr, "рядків: %llu, байтів проскочено вхолосту: %llu\n",
                 static_cast<unsigned long long>(rows),
                 static_cast<unsigned long long>(slides));
    return 0;
}
