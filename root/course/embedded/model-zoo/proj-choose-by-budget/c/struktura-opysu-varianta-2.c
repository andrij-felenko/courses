// Таблиця ПІД КОНКРЕТНИЙ чип. Порядок: від найбільшого (x) до найменшого (n).
// latency_us тут — ПРИКЛАД виміряних чисел; на іншому залізі вони інші.
// Саме тому таблиця — дані, а не зашите в код "беремо s".
static const ModelVariant kFamily[] = {
//   name  model_data       model_bytes  arena_bytes  mAP×100  latency_us(p99)
    {"x",  g_yolov8x_int8,  68u*1024*1024, 512u*1024,   5390,   210000},  // 210 мс
    {"l",  g_yolov8l_int8,  44u*1024*1024, 384u*1024,   5290,   150000},  // 150 мс
    {"m",  g_yolov8m_int8,  26u*1024*1024, 256u*1024,   5020,    95000},  //  95 мс
    {"s",  g_yolov8s_int8,  11u*1024*1024, 160u*1024,   4490,    55000},  //  55 мс
    {"n",  g_yolov8n_int8,   3u*1024*1024,  96u*1024,   3730,    28000},  //  28 мс
};
static const int kFamilyCount = (int)(sizeof(kFamily) / sizeof(kFamily[0]));
