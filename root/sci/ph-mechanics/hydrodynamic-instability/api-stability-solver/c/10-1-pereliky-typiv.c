typedef enum {
    HYDRO_BC_RIGID_WALL   = 0,  /* Тверді стінки з прилипанням: ϕ(±1) = 0, ϕ'(±1) = 0 */
    HYDRO_BC_FREE_SLIP    = 1,  /* Вільне ковзання без дотичного напруження: ϕ(±1) = 0, ϕ''(±1) = 0 */
    HYDRO_BC_PERIODIC     = 2,  /* Періодичні умови для вільного зсувного шару */
    HYDRO_BC_FREE_SURFACE = 3   /* Вільна поверхня з капілярним напруженням */
} hydro_bc_type_t;

typedef enum {
    HYDRO_SOLVER_QZ_LAPACK     = 0, /* Повний QZ алгоритм LAPACK (zggev) для всіх значень */
    HYDRO_SOLVER_ARNOLDI_ARPACK = 1  /* Ітераційний метод Арнольді (ARPACK) для найнебезпечніших мод */
} hydro_solver_algo_t;

typedef enum {
    HYDRO_LOG_NONE  = 0,  /* Логування вимкнено */
    HYDRO_LOG_INFO  = 1,  /* Інформаційні повідомлення про перебіг обчислень */
    HYDRO_LOG_DEBUG = 2   /* Докладна налагоджувальна інформація та норми матриць */
} hydro_log_level_t;
