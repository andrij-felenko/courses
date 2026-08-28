// ПРИМІТИВ 4 — робоча черга + пул.  Суть: черга (один таск — один виконавець),
// але воркери біжать ПО-СПРАВЖНЬОМУ паралельно; спільну чергу стереже м'ютекс —
// саме він арбітрує, кому дістанеться наступний таск.
#include <queue>
#include <mutex>
#include <thread>
#include <vector>
#include <functional>

template <class T>
class WorkQueue {
  std::queue<T> buf;
  std::mutex m;                                  // вартовий спільної черги
public:
  void submit(T job) { buf.push(std::move(job)); }   // усе кладемо ДО drain

  void drain(int workers, std::function<void(const T&, int)> handle) {
    auto run = [&](int id) {
      for (;;) {
        T job;
        {
          std::lock_guard<std::mutex> lock(m);   // у черзі — лише ОДИН воркер за раз
          if (buf.empty()) return;               // тасків більше нема — воркер виходить
          job = std::move(buf.front());
          buf.pop();                             // вихопив — більше нікому не дістанеться
        }
        handle(job, id);                         // працюємо ПОЗА замком — справді паралельно
      }
    };
    std::vector<std::thread> pool;
    for (int id = 0; id < workers; ++id) pool.emplace_back(run, id);
    for (auto& t : pool) t.join();               // дочекатися всіх
  }
};
