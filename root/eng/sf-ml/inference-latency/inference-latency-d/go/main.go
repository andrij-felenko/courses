package main

import "time"

// model_infer робить один прохід; g_input / g_output — вхід і вихід моделі.

func measureLatency() {
    const N = 200

    // 1) Прогрів: перші прогони завжди повільніші (кеш холодний,
    //    залізо ще не «розкрутилось»). Їх у статистику НЕ беремо.
    for i := 0; i < 20; i++ {
        modelInfer(gInput, gOutput)
    }

    // 2) Заміри: кожен прохід — окремо, щоб бачити РОЗКИД, не лише суму.
    var worst, sum time.Duration
    for i := 0; i < N; i++ {
        t0 := time.Now()
        modelInfer(gInput, gOutput)
        dt := time.Since(t0) // латентність цього кадру (монотонний годинник)

        sum += dt
        if dt > worst {
            worst = dt // стежимо за ХВОСТОМ
        }
    }

    mean := sum / N
    // mean  — типова латентність; worst — найгірший кадр (наближення до p99).
    // Для бюджету 30 к/с придатність вирішує саме worst, а не mean:
    //   worst < 33*time.Millisecond  →  укладаємось навіть у найгіршому кадрі.
    report(mean, worst)
}
