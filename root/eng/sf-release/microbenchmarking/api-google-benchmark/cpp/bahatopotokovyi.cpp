static void BM_ConcurrentQueue(benchmark::State& state) {
    static LockFreeQueue queue;
    for (auto _ : state) {
        if (state.thread_index() == 0) {
            queue.push(42);
        } else {
            queue.pop();
        }
    }
}
BENCHMARK(BM_ConcurrentQueue)->ThreadRange(1, 16)->UseRealTime();
