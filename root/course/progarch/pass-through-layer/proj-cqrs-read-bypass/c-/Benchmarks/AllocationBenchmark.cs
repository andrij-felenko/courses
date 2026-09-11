using System;
using System.Diagnostics;
using DigitalHomes.ClimateControl.Application;

namespace DigitalHomes.ClimateControl.Benchmarks;

/// <summary>
/// Бенчмарк для вимірювання виділення пам'яті в купі (Heap Allocations)
/// та продуктивності між Pass-Through Layer і Dapper Bypass Channel.
/// </summary>
public static class AllocationBenchmark
{
    public static void Run(
        PassThroughClimateService passThroughService,
        DapperClimateQueries bypassQueries,
        int iterations = 10_000)
    {
        Console.WriteLine($"=== Запуск бенчмарку виділення пам'яті ({iterations:N0} ітерацій) ===");
        Console.WriteLine("Прогрів JIT-компілятора...");

        // Прогрів JIT
        for (int i = 0; i < 100; i++)
        {
            _ = passThroughService.GetClimateDashboard();
            _ = bypassQueries.GetClimateDashboard();
        }

        // 1. Тест транзитного шару (Pass-Through Layer)
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();

        long passThroughGen0Before = GC.CollectionCount(0);
        long passThroughAllocBefore = GC.GetAllocatedBytesForCurrentThread();
        var sw = Stopwatch.StartNew();

        for (int i = 0; i < iterations; i++)
        {
            _ = passThroughService.GetClimateDashboard();
        }

        sw.Stop();
        long passThroughElapsedMs = sw.ElapsedMilliseconds;
        long passThroughAllocAfter = GC.GetAllocatedBytesForCurrentThread();
        long passThroughGen0After = GC.CollectionCount(0);

        long passThroughTotalBytes = passThroughAllocAfter - passThroughAllocBefore;
        long passThroughGen0Count = passThroughGen0After - passThroughGen0Before;
        double passThroughBytesPerOp = (double)passThroughTotalBytes / iterations;

        // 2. Тест каналу обходу (Dapper Bypass Channel)
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();

        long bypassGen0Before = GC.CollectionCount(0);
        long bypassAllocBefore = GC.GetAllocatedBytesForCurrentThread();
        sw.Restart();

        for (int i = 0; i < iterations; i++)
        {
            _ = bypassQueries.GetClimateDashboard();
        }

        sw.Stop();
        long bypassElapsedMs = sw.ElapsedMilliseconds;
        long bypassAllocAfter = GC.GetAllocatedBytesForCurrentThread();
        long bypassGen0After = GC.CollectionCount(0);

        long bypassTotalBytes = bypassAllocAfter - bypassAllocBefore;
        long bypassGen0Count = bypassGen0After - bypassGen0Before;
        double bypassBytesPerOp = (double)bypassTotalBytes / iterations;

        // 3. Виведення результатів
        Console.WriteLine();
        Console.WriteLine("+-----------------------------+--------------------+--------------------+-------------------+");
        Console.WriteLine("| Показник                    | Pass-Through Layer | Dapper CQRS Bypass | Різниця (виграш)  |");
        Console.WriteLine("+-----------------------------+--------------------+--------------------+-------------------+");
        Console.WriteLine($"| Загальний час               | {passThroughElapsedMs,14} мс | {bypassElapsedMs,14} мс | {((double)passThroughElapsedMs / Math.Max(1, bypassElapsedMs)):F1}x швидше      |");
        Console.WriteLine($"| Виділена пам'ять (разом)    | {passThroughTotalBytes / (1024.0 * 1024.0),13:F2} МБ | {bypassTotalBytes / (1024.0 * 1024.0),13:F2} МБ | {((double)passThroughTotalBytes / Math.Max(1, bypassTotalBytes)):F1}x менше пам'яті |");
        Console.WriteLine($"| Пам'ять на 1 запит          | {passThroughBytesPerOp,15:F0} Б | {bypassBytesPerOp,15:F0} Б | {((double)passThroughBytesPerOp / Math.Max(1, bypassBytesPerOp)):F1}x менше        |");
        Console.WriteLine($"| Збирань сміття Gen 0        | {passThroughGen0Count,18} | {bypassGen0Count,18} | {passThroughGen0Count - bypassGen0Count} збережених пауз |");
        Console.WriteLine("+-----------------------------+--------------------+--------------------+-------------------+");
        Console.WriteLine();
        Console.WriteLine("ВИСНОВОК: Транзитний шар (Pass-Through) витрачає ресурси на інстанціювання");
        Console.WriteLine("доменних сутностей і проміжний мапінг, які не несуть користі для читання.");
        Console.WriteLine("Прямий Dapper-канал обходу радикально знижує навантаження на GC і підвищує швидкість.");
    }
}
