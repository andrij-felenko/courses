typedef void (*Step)(void);

void step_blink(void);
void step_sensor(void);
void step_uart(void);

static Step steps[] = { step_blink, step_sensor, step_uart };
enum { N_STEPS = sizeof(steps) / sizeof(steps[0]) };

void loop(void) {
    for (int i = 0; i < N_STEPS; i++)
        steps[i]();          // кожен крок — коротко, і одразу return
}
