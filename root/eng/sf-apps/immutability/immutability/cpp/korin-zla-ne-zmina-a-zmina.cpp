struct Config {
    int  timeout;
    bool verbose;
};

void tweak(Config& c) {   // приймає посилання — тобто АЛІАС чужого об'єкта
    c.timeout = 0;        // "тимчасово вимкну таймаут для свого тесту"
}

Config base{ 30, false };
Config& shortcut = base;  // ще один аліас на той самий base
tweak(shortcut);
// base.timeout уже 0, хоча "base" ми ніби не чіпали
