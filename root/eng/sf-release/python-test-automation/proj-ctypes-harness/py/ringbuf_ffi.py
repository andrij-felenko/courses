# ringbuf_ffi.py — єдине місце, де описано домовленість із libringbuf
import ctypes, os, sys

u8   = ctypes.c_uint8
u8p  = ctypes.POINTER(ctypes.c_uint8)
size = ctypes.c_size_t


class RB(ctypes.Structure):
    """Дзеркало struct rb. Порядок і типи полів мусять збігатися точно."""
    _fields_ = [
        ("data",      u8p),
        ("cap",       size),
        ("head",      size),
        ("tail",      size),
        ("len",       size),
        ("owns_data", u8),
        ("overrun",   u8),
    ]


RBp = ctypes.POINTER(RB)


def _libname():
    if sys.platform == "win32":  return "ringbuf.dll"
    if sys.platform == "darwin": return "libringbuf.dylib"
    return "libringbuf.so"


lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), _libname()))

lib.rb_create.argtypes        = [size];        lib.rb_create.restype        = RBp
lib.rb_create_static.argtypes = [u8p, size];   lib.rb_create_static.restype = RBp
lib.rb_init.argtypes          = [RBp, u8p, size]; lib.rb_init.restype       = None
lib.rb_destroy.argtypes       = [RBp];         lib.rb_destroy.restype       = None
lib.rb_push.argtypes          = [RBp, u8];     lib.rb_push.restype          = ctypes.c_int
lib.rb_pop.argtypes           = [RBp, u8p];    lib.rb_pop.restype           = ctypes.c_int
lib.rb_len.argtypes           = [RBp];         lib.rb_len.restype           = size
lib.rb_sizeof.argtypes        = [];            lib.rb_sizeof.restype        = size
lib.rb_offset.argtypes        = [ctypes.c_char_p]; lib.rb_offset.restype    = size
