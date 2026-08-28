typedef struct {
    double timestamp;             /* поточний час оцінки, с */
    MsckfVec3 position;           /* положення корпусу у світовій системі, м */
    MsckfVec3 velocity;           /* лінійна швидкість корпусу, м/с */
    MsckfQuat orientation;        /* орієнтація корпусу (світ -> корпус) */
    MsckfVec3 gyro_bias;          /* поточна оцінка зсуву гіроскопа, рад/с */
    MsckfVec3 accel_bias;         /* поточна оцінка зсуву акселерометра, м/с² */
    
    /* Діагональ матриці коваріацій (СКП похибок) */
    MsckfVec3 pos_std;            /* невизначеність положення, м */
    MsckfVec3 vel_std;            /* невизначеність швидкості, м/с */
    MsckfVec3 att_std;            /* невизначеність кутів орієнтації, рад */
} MsckfEstimate;

typedef struct {
    uint32_t current_window_size; /* кількість активних поз у вікні */
    uint32_t active_tracks_count; /* кількість точок, що супроводжуються */
    uint32_t updated_features;    /* кількість орієнтирів, утилізованих у корекції */
    uint32_t rejected_outliers;   /* кількість викидів, відсіяних тестом χ² */
    bool is_initialized;          /* чи завершено початкове вирівнювання гравітації */
} MsckfDiagnostics;
