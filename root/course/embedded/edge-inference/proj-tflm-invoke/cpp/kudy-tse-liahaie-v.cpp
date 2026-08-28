int main(void) {
    hardware_init();                 // тактування, GPIO, давач
    cycle_counter_init();            // увімкнути DWT->CYCCNT (раз)

    if (!model_init()) {             // усі запобіжники старту всередині
        MicroPrintf("model_init failed — inference disabled");
        fault_blink();               // не вдаємо, що працюємо: чесно сигналимо
    }

    for (;;) {                       // super-loop
        if (sensor_frame_ready()) {
            float frame[kFeatureCount];
            sensor_read_frame(frame, kFeatureCount);

            float p = model_run(frame, kFeatureCount);
            if (p >= 0.0f) {                       // −1 = збій проходу
                MicroPrintf("p=%d/1000  %u us",
                            (int)(p * 1000), last_latency_us());
                if (p > 0.8f) on_detection();      // спрацювала умова
            }
        }
        // ... решта super-loop: інша периферія, керування живленням ...
    }
}
