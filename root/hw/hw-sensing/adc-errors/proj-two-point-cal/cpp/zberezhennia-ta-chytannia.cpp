Preferences prefs;

void saveCalib(const Calib& c) {
    prefs.begin("adccal", false);   // false = читання-запис
    prefs.putInt  ("rawLo", c.rawLo);
    prefs.putInt  ("rawHi", c.rawHi);
    prefs.putFloat("vLo",   c.vLo);
    prefs.putFloat("vHi",   c.vHi);
    prefs.end();
}

bool loadCalib(Calib& c) {
    prefs.begin("adccal", true);    // true = тільки читання
    if (!prefs.isKey("rawLo")) {    // ще жодного разу не калібрували
        prefs.end();
        return false;
    }
    c.rawLo = prefs.getInt  ("rawLo");
    c.rawHi = prefs.getInt  ("rawHi");
    c.vLo   = prefs.getFloat("vLo");
    c.vHi   = prefs.getFloat("vHi");
    prefs.end();
    return true;
}
