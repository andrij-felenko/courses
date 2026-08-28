// 1. Поодинокі аргументи або фіксовані списки розмірів
BENCHMARK(BM_Sort)->Arg(100)->Arg(1000)->Arg(10000);
BENCHMARK(BM_MatrixMul)->Args({32, 32})->Args({64, 64});

// 2. Геометрична шкала: від 8 до 8192 з множником 8 (8, 64, 512, 4096)
BENCHMARK(BM_Lookup)->RangeMultiplier(8)->Range(8, 8192);

// 3. Декартовий добуток діапазонів (2D/3D матриця параметрів)
BENCHMARK(BM_Transform)->ArgsProduct({
    benchmark::CreateRange(8, 512, 8),
    {1, 2, 4, 8} // кількість потоків або каналів
});

// 4. Налаштування тривалості, повторів та статистичної агрегації
BENCHMARK(BM_NetworkSend)
    ->MinTime(1.5)                 // Мінімальний час прогону (1.5 секунди)
    ->Repetitions(10)              // 10 незалежних прогонів для статистики
    ->ReportAggregatesOnly(true)   // Виводити лише Mean/Median/StdDev
    ->DisplayAggregatesOnly(true);
