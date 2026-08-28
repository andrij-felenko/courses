# 1. Компіляція утиліти на C та C++
$ gcc -Wall -Wextra trace_reader.c -o trace_reader_c
$ g++ -Wall -Wextra -std=c++20 trace_reader.cpp -o trace_reader_cpp

# 2. Увімкнення статичної точки трасування sched_switch у tracefs
$ echo 1 | sudo tee /sys/kernel/tracing/events/sched/sched_switch/enable

# 3. Запуск C або C++ утиліти моніторингу подій
$ sudo ./trace_reader_cpp

# 4. Після завершення спостереження вимкнути точку трасування
$ echo 0 | sudo tee /sys/kernel/tracing/events/sched/sched_switch/enable
