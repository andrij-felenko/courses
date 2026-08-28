struct AsMut   { static constexpr const char* who = "data()";       };
struct AsConst { static constexpr const char* who = "data() const"; };

struct Buf {
    AsMut   data()       { return {}; }   // неявний параметр: Buf&
    AsConst data() const { return {}; }   // неявний параметр: const Buf&
};

Buf b;
const Buf& cb = b;

SHOW( b.data()  );
SHOW( cb.data() );
