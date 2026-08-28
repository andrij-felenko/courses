import time

# model_infer(input, output) — один прохід; g_input / g_output — вхід і вихід.
# time.perf_counter_ns — монотонний годинник високої роздільності.

def measure_latency():
    N = 200

    # 1) Прогрів: перші прогони завжди повільніші (кеш холодний,
    #    залізо ще не «розкрутилось»). Їх у статистику НЕ беремо.
    for _ in range(20):
        model_infer(g_input, g_output)

    # 2) Заміри: кожен прохід — окремо, щоб бачити РОЗКИД, не лише суму.
    worst = 0
    total = 0
    for _ in range(N):
        t0 = time.perf_counter_ns()
        model_infer(g_input, g_output)
        dt = (time.perf_counter_ns() - t0) // 1000   # латентність цього кадру, мкс

        total += dt
        worst = max(worst, dt)                        # стежимо за ХВОСТОМ

    mean = total // N
    # mean  — типова латентність; worst — найгірший кадр (наближення до p99).
    # Для бюджету 30 к/с придатність вирішує саме worst, а не mean:
    #   worst < 33000 мкс  →  укладаємось навіть у найгіршому кадрі.
    report(mean, worst)
