// PAL-розгортка: рахунок таймінгу рядка у прошивці
const int   lines_per_frame = 625;
const float frames_per_sec  = 25.0f;

float line_rate = lines_per_frame * frames_per_sec; // = 15625 рядків/с
float line_time = 1.0f / line_rate;                 // = 64.0 мкс на рядок

// скільки точок устигне піксельний такт 8 МГц за активну частину рядка
// (з 64 мкс близько 52 мкс — активне відео, решта — синхро + гасіння)
const float pixel_clock = 8.0e6f;        // 8 МГц
float active_time = 52.0e-6f;            // активна частина рядка, с
int   dots = (int)(pixel_clock * active_time); // = 416 точок уздовж рядка
