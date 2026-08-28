clang++ -fsanitize=thread -g -O1 bank_account.cpp -o bank_test
./bank_test
# Вивід ThreadSanitizer:
WARNING: ThreadSanitizer: data race (pid=41920)
  Write of size 8 at 0x7ffd9b8f2140 by thread T2:
    #0 Counter::increment() counter.cpp:14 (bank_test+0x49a120)
    #1 worker_thread(void*) counter.cpp:28 (bank_test+0x49a340)

  Previous Read of size 8 at 0x7ffd9b8f2140 by thread T1:
    #0 Counter::get_value() counter.cpp:18 (bank_test+0x49a180)
    #1 monitor_thread(void*) counter.cpp:35 (bank_test+0x49a3c0)

  Location is stack of main thread at 0x7ffd9b8f2140.
SUMMARY: ThreadSanitizer: data race counter.cpp:14 in Counter::increment()
