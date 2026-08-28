// media.h, 2009 рік. Коментарі — увесь контракт, який був.
struct Codec;
struct Frame;
struct Sink;

Codec* make_codec(const char* fourcc);      // 0, якщо кодек невідомий
void   free_codec(Codec* c);
void   set_sink(Codec* c, Sink* s);         // «sink лишається за вами»
bool   probe(Codec* c, const Frame* f);     // f можна 0
void   submit(Codec* c, const Frame* f);    // декодує в робочому потоці
Codec* current_codec();                     // 0, поки нічого не відкрито
