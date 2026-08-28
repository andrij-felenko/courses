from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("""
    typedef struct {
        int32_t x;
        int32_t y;
        double  weight;
        uint8_t flags;
        ...; /* cffi самостійно розрахує вирівнювання через C-компілятор */
    } PointRecord;

    typedef union {
        uint32_t as_uint;
        float    as_float;
        uint8_t  as_bytes[4];
    } FloatIntUnion;
""")
