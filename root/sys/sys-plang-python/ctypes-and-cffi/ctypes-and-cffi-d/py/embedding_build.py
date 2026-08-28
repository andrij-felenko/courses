# embedding_build.py
from cffi import FFI

ffibuilder = FFI()

ffibuilder.embedding_api("""
    int calculate_checksum(const char *data, int len);
""")

ffibuilder.embedding_init_code("""
    from _embedded_lib import ffi

    @ffi.def_extern()
    def calculate_checksum(data, length):
        raw_bytes = ffi.buffer(data, length)[:]
        return sum(raw_bytes) % 256
""")

ffibuilder.set_source("_embedded_lib", "")
ffibuilder.compile(target="libchecksum.so", verbose=True)
