// model_input, model_output — вказівники на тензори інтерпретатора TFLM
// (той самий скелет, що в темі про інференс: AllocateTensors один раз при старті).

float anomaly_score(const float *feat)
{
    for (int i = 0; i < N_BANDS; i++)
        model_input[i] = feat[i];        // вхід автокодера

    interpreter->Invoke();               // прохід: детермінований, сталий за часом

    // Похибка відновлення = наскільки вихід розійшовся зі входом (MSE).
    float err = 0.0f;
    for (int i = 0; i < N_BANDS; i++) {
        float d = feat[i] - model_output[i];
        err += d * d;
    }
    return err / N_BANDS;
}

// У super-loop: поріг THRESHOLD підібрано на записі здорової роботи.
if (anomaly_score(feat) > THRESHOLD) {
    raise_alarm();                       // світлодіод, або один пакет по радіо
}
