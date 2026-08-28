static float noise = 50.0f;        // початкова груба оцінка фону
const float ALPHA  = 0.02f;        // повільне середнє: важке, інертне
const float MARGIN = 3.0f;         // поріг = фон × запас

bool detect(float rms) {
    float threshold = noise * MARGIN;
    bool  event = (rms > threshold);

    if (!event) {                  // оновлюємо фон ТІЛЬКИ в тиші
        noise += ALPHA * (rms - noise);
    }
    return event;
}
