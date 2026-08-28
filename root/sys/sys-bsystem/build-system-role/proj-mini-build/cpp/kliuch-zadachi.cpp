// Ключ — геш усього, від чого залежить результат.
// 0 означає «ключа немає»: якийсь вхід не читається, отже про актуальність не йдеться.
static uint64_t taskKey(const Rule& r) {
    Fnv h;
    h.feed("mb/1");            h.sep();   // версія схеми ключа
    h.feed(r.out);             h.sep();
    h.feed(expand(r, r.out));  h.sep();   // команда з підставленим СПРАВЖНІМ виходом
    for (const auto& in : r.ins) {
        h.feed(in);            h.sep();
        if (!hashFile(in, h)) return 0;
        h.sep();
    }
    return h.h ? h.h : 1;                 // нуль бережемо під «немає»
}
