// Радар як дані: кожен блип — назва, кільце, квадрант.
// Найпростіша форма — таблиця, яку легко тримати поряд із кодом.
typedef enum { ADOPT, TRIAL, ASSESS, HOLD } Ring;

typedef struct {
    const char* name;    // напр. ідентифікатор бібліотеки/пакета
    Ring        ring;    // куди команда його поклала
} Blip;

static const Blip RADAR[] = {
    { "grpc",         ADOPT  },
    { "kafka",        ADOPT  },
    { "postgres",     ADOPT  },
    { "rabbitmq",     TRIAL  },
    { "mongo",        ASSESS },
    { "soap-legacy",  HOLD   },   // від цього відходимо
    { "custom-queue", HOLD   },   // самописна черга — більше нового не заводимо
};
static const int RADAR_N = sizeof(RADAR) / sizeof(RADAR[0]);

// Знайти кільце технології за назвою; -1, якщо її на радарі нема взагалі.
static int ring_of(const char* dep) {
    for (int i = 0; i < RADAR_N; ++i)
        if (strcmp(RADAR[i].name, dep) == 0)
            return (int)RADAR[i].ring;
    return -1;   // не на радарі — окремий випадок, теж вартий уваги
}
