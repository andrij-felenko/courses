#include "boundary_benchmarks.hpp"
#include <benchmark/benchmark.h>
#include <thread>

namespace boundary_benchmarks {

ResponsePayload DirectCalculator::compute(const RequestPayload& req) {
    return executeBusinessLogic(req);
}

ResponsePayload DirectCalculator::computeDirect(const RequestPayload& req) const noexcept {
    return executeBusinessLogic(req);
}

// 1. Бенчмарк: прямий виклик функції (Direct Call)
// Базова лінія: наносекунди, прямий машинний перехід за адресою без посередників
static void BM_DirectFunctionCall(benchmark::State& state) {
    DirectCalculator calc;
    RequestPayload req{.id = 42, .value = 123.456, .tag = "direct_test"};

    for (auto _ : state) {
        ResponsePayload res = calc.computeDirect(req);
        benchmark::DoNotOptimize(res);
        req.id++;
    }
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_DirectFunctionCall);

// 2. Бенчмарк: поліморфний виклик через таблицю віртуальних методів (vtable)
// Перетин межі модульності всередині процесу: розіменування покажчика vtable та непрямий виклик
static void BM_VtableVirtualCall(benchmark::State& state) {
    std::unique_ptr<ICalculator> calc = std::make_unique<DirectCalculator>();
    RequestPayload req{.id = 42, .value = 123.456, .tag = "vtable_test"};

    for (auto _ : state) {
        ResponsePayload res = calc->compute(req);
        benchmark::DoNotOptimize(res);
        req.id++;
    }
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_VtableVirtualCall);

// 3. Бенчмарк: міжпотоковий перетин межі через чергу повідомлень (std::jthread)
// Перетин межі потоків: синхронізація кеш-ліній CPU, м'ютекси, condition_variable
static void BM_ThreadQueueHandoff(benchmark::State& state) {
    ThreadSafeQueue<RequestPayload> requestQueue;
    ThreadSafeQueue<ResponsePayload> responseQueue;

    // Фоновий потік-обробник (робочий потік)
    std::jthread worker([&](std::stop_token st) {
        while (!st.stop_requested()) {
            auto reqOpt = requestQueue.pop();
            if (!reqOpt) {
                break;
            }
            ResponsePayload res = executeBusinessLogic(*reqOpt);
            responseQueue.push(res);
        }
    });

    RequestPayload req{.id = 1, .value = 99.9, .tag = "thread_test"};

    for (auto _ : state) {
        requestQueue.push(req);
        auto res = responseQueue.pop();
        benchmark::DoNotOptimize(res);
        req.id++;
    }

    requestQueue.stop();
    responseQueue.stop();
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_ThreadQueueHandoff);

} // namespace boundary_benchmarks
