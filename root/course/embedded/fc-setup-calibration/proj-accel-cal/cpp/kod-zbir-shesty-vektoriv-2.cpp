// шість положень у фіксованому порядку — рушій знатиме, який вектор до якого належить
enum { FACE_LEVEL, FACE_LEFT, FACE_RIGHT, FACE_NOSEDOWN, FACE_NOSEUP, FACE_BACK, N_FACES };

static const char *face_prompt[N_FACES] = {
    "рівно (Z вгору)", "на лівий бік", "на правий бік",
    "носом униз",      "носом угору",  "на спину (Z вниз)"
};

// Зібрати всі шість усереднених векторів. samples[i] — грань i.
static bool accel_collect_six(vec3_t samples[N_FACES])
{
    for (int f = 0; f < N_FACES; f++) {
        gcs_prompt(face_prompt[f]);       // «поставте апарат …» на станцію
        wait_operator_click();            // оператор поставив і натиснув «зняти»

        // перезнімаємо доти, доки грань не знято нерухомо
        while (!accel_capture_face(&samples[f])) {
            gcs_prompt("апарат рухався — завмріть і натисніть ще раз");
            wait_operator_click();
        }
    }
    return true;
}
