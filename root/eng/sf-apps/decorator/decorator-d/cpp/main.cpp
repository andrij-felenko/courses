// кожен шар — окремий віртуальний виклик: N шарів = N непрямих переходів
struct Reader { virtual int read() = 0; virtual ~Reader() = default; };

struct Counting : Reader {
    Reader* inner;
    long n = 0;
    int read() override { ++n; return inner->read(); }  // стрибок за vptr до inner
};
// читання крізь 5 шарів = 5 віртуальних викликів на КОЖЕН read():
//   стрибок за вказівником vtable, промах інлайнінгу, гірша локальність коду
