# fastmath_build.py
from cffi import FFI

ffibuilder = FFI()

# Оголошуємо сигнатури C-інтерфейсу
ffibuilder.cdef("""
    typedef struct {
        double x;
        double y;
        double z;
        uint32_t id;
    } Point3D;

    uint32_t fast_crc32_step(uint32_t crc, uint8_t byte);
    void vector_scale(double *data, size_t size, double factor);
    void transform_point(Point3D *pt, double dx, double dy, double dz);
""")

# Задаємо параметри включення заголовків та лінкування
ffibuilder.set_source(
    "_fastmath_cffi",
    """
    #include "fastmath.h"
    """,
    libraries=["fastmath"],
    library_dirs=["."],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
