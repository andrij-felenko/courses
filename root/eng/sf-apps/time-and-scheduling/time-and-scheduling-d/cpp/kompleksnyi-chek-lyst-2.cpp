/* Прив'язка потоку до виділеного ядра та RT-пріоритет (C++20) */
void configure_realtime_thread(std::jthread& th, int core_id, int priority = 99) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(th.native_handle(), sizeof(cpu_set_t), &cpuset);

    sched_param param{.sched_priority = priority};
    pthread_setschedparam(th.native_handle(), SCHED_FIFO, &param);
}
