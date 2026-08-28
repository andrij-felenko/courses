std::packaged_task<int()> task([] { return 42; });
std::shared_future<int> shared_fut = task.get_future().share();

// Декілька потоків можуть безпечно викликати shared_fut.get() паралельно!
std::thread t1([shared_fut] { std::cout << "T1: " << shared_fut.get() << "\n"; });
std::thread t2([shared_fut] { std::cout << "T2: " << shared_fut.get() << "\n"; });

task();
t1.join();
t2.join();
