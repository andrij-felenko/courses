typedef struct {
    double *time_lags;          /* Масив часових затримок τ, с */
    double *msd_values;         /* Обчислені значення MSD <Δr²(τ)>, м² */
    double *std_errors;         /* Стандартні помилки MSD */
    size_t num_lags;            /* Кількість порахованих часових затримок */
    double estimated_D;         /* Оцінений коефіцієнт дифузії D, м²/с */
    double r_squared;           /* Якість лінійної апроксимації (R²) */
    double anomalous_exponent;  /* Показник аномальності α (<r²> ~ τ^α) */
    int status_code;            /* Код стану або помилки обчислень */
} BrownianMsdResult;
