std::atomic<bool> ready{false};
int data = 0;                              // звичайна змінна, не atomic

// потік-виробник
data = 42;                                 // 1) готуємо дані
ready.store(true, std::memory_order_release);   // 2) release-прапорець

// потік-споживач
while (!ready.load(std::memory_order_acquire)) { }  // чекаємо acquire-читанням
use(data);                                 // тут data ГАРАНТОВАНО == 42
