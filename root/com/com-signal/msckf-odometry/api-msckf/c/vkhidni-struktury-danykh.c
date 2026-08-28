typedef struct {
    double timestamp;             /* секунди */
    MsckfVec3 linear_accel;       /* покази акселерометра, м/с² */
    MsckfVec3 angular_vel;        /* покази гіроскопа, рад/с */
} MsckfImuMeasurement;

typedef struct {
    uint32_t feature_id;          /* унікальний глобальний ідентифікатор треку */
    double u, v;                  /* нормовані координати на площині камери */
} MsckfFeaturePoint;

typedef struct {
    double timestamp;             /* час експозиції кадру, с */
    uint32_t num_features;        /* кількість точок у поточному кадрі */
    const MsckfFeaturePoint* features;
} MsckfFeatureFrame;
