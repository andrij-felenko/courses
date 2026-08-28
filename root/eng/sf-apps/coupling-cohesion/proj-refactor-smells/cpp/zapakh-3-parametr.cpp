private:
    bool rawWrite(const uint8_t* data, size_t len) {   // спільне ядро
        return file_.write(data, len) == len;
    }
public:
    // Швидкий шлях — ім'я каже саме за себе
    bool logRecord(const uint8_t* data, size_t len) {
        return rawWrite(data, len);
    }
    // Надійний шлях — окрема функція, окрема гарантія
    bool commitRecord(const uint8_t* data, size_t len) {
        if (!rawWrite(data, len)) return false;
        file_.sync();
        return verifyLastWrite(data, len);
    }
