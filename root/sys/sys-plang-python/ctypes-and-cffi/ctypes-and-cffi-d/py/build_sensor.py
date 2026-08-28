# build_sensor.py
from cffi import FFI

ffibuilder = FFI()

ffibuilder.cdef("""
    typedef struct {
        int sensor_id;
        double calibration_factor;
        ...; /* Невідомі або внутрішні поля та вирівнювання */
    } SensorData;

    int read_sensor(SensorData *dev);
""")

ffibuilder.set_source(
    "_sensor_backend",
    """
    #include <sensor_driver.h>
    """,
    libraries=["sensor_driver"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
