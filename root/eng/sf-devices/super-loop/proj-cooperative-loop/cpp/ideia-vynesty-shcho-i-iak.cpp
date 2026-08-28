typedef void (*Job)(void);          // дія — функція без аргументів

typedef struct {
    unsigned long period;           // інтервал, мс
    unsigned long last;             // коли востаннє спрацювала, мс
    Job           fn;               // що виконати
} Task;

Task tasks[] = {
    { 1000, 0, toggleLed    },      // блимати щосекунди
    {  200, 0, readSensor    },     // читати 5 разів/с
    { 5000, 0, sendHeartbeat },     // серцебиття раз на 5 с
};
const int N = sizeof(tasks) / sizeof(tasks[0]);
