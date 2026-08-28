typedef struct optionblk {
    boolean getcanon;      /* TRUE: обчислити канонічний граф canon */
    boolean digraph;       /* TRUE: орієнтований граф; FALSE: неорієнтований */
    boolean writeautoms;   /* TRUE: друкувати генератори Aut(G) у stdout */
    boolean writemarkers;  /* TRUE: друкувати маркери дерева пошуку */
    int defaultptn;        /* TRUE: початкове розбиття є тотожно дискретним */
    int cartesian;         /* Налаштування обчислення векторних продуктів */
    int linelength;        /* Довжина рядка при виводі */
    FILE *outfile;         /* Потік для текстового виводу результатів */
    void (*userrefproc)(void*, int*, int*, int, int*, int*, set*, int*, int, int);
    void (*userautomproc)(int, int*, int*, int, int, int);
    void (*userlevelproc)(int*, int*, int, int*, int*, int, int, int);
    void (*nodeaction)(graph*, int*, int*, int, int, int, int);
    boolean tc_degree;     /* Пріоритет вибору цільового осередку за степенями */
    boolean minvarbyfreq;  /* Варіація інваріанта за частотою кольорів */
    int maxinvarlevel;     /* Максимальний рівень використання важких інваріантів */
    int invararg;          /* Додатковий параметр інваріанта */
} optionblk;
