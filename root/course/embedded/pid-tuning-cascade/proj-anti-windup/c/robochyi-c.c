void pid_init(pid_t *p,
              float Kp, float Ki, float Kd,
              float u_min, float u_max, float N)
{
    p->Kp = Kp; p->Ki = Ki; p->Kd = Kd;
    p->u_min = u_min; p->u_max = u_max;
    p->N = N;

    // здорові типові значення захистів:
    p->aw   = AW_CLAMP;           // затиск за замовчуванням — простий і надійний
    p->Kaw  = (Kp != 0.0f) ? Ki / Kp : 0.0f;  // орієнтир Tt≈√(Ti·Td) → Kaw≈Ki/Kp
    p->b    = 1.0f;               // повна реакція P на завдання
    p->c    = 0.0f;               // похідна ТІЛЬКИ від виміру (нема кіку)

    // стан — у нуль; initialized=false, щоб перший крок обробився окремо:
    p->integral   = 0.0f;
    p->meas_prev  = 0.0f;
    p->deriv_filt = 0.0f;
    p->initialized = false;
}
