import heapq
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List

class EventType(Enum):
    ARRIVAL = 1
    DEPARTURE = 2

class Discipline(Enum):
    FIFO = 1
    LIFO = 2

@dataclass(order=True)
class Event:
    time: float
    event_type: EventType = field(compare=False)
    req_id: int = field(compare=False)
    arrive_time: float = field(compare=False)

class QueueSimulator:
    def __init__(self, arrival_rate: float, service_rate: float, 
                 discipline: Discipline = Discipline.FIFO, heavy_tailed: bool = False):
        self.lam = arrival_rate
        self.mu = service_rate
        self.discipline = discipline
        self.heavy_tailed = heavy_tailed
        self.rng = random.Random(1337)

    def next_service_time(self) -> float:
        if not self.heavy_tailed:
            return self.rng.expovariate(self.mu)
        # Парето розподіл із середнім 1/mu (alpha = 1.5)
        alpha = 1.5
        xm = (alpha - 1.0) / alpha * (1.0 / self.mu)
        return self.rng.paretovariate(alpha) * xm

    def run(self, max_time: float):
        current_time = 0.0
        last_event_time = 0.0
        in_system_count = 0
        area_n = 0.0
        completed_requests = 0
        total_residence_time = 0.0
        server_busy = False
        next_req_id = 1

        event_queue: List[Event] = []
        waiting_queue: List[tuple[int, float]] = []

        # Перше надходження
        first_arrive = self.rng.expovariate(self.lam)
        heapq.heappush(event_queue, Event(first_arrive, EventType.ARRIVAL, next_req_id, first_arrive))
        next_req_id += 1

        while event_queue and current_time < max_time:
            ev = heapq.heappop(event_queue)
            
            # Оновлюємо інтеграл кількості заявок у часі
            dt = ev.time - last_event_time
            area_n += in_system_count * dt
            current_time = ev.time
            last_event_time = ev.time

            if ev.event_type == EventType.ARRIVAL:
                in_system_count += 1
                if not server_busy:
                    server_busy = True
                    st = self.next_service_time()
                    heapq.heappush(event_queue, Event(current_time + st, EventType.DEPARTURE, ev.req_id, ev.arrive_time))
                else:
                    waiting_queue.append((ev.req_id, ev.arrive_time))

                # Плануємо наступне надходження
                next_arr_time = current_time + self.rng.expovariate(self.lam)
                heapq.heappush(event_queue, Event(next_arr_time, EventType.ARRIVAL, next_req_id, next_arr_time))
                next_req_id += 1

            elif ev.event_type == EventType.DEPARTURE:
                in_system_count -= 1
                completed_requests += 1
                total_residence_time += (current_time - ev.arrive_time)

                if waiting_queue:
                    if self.discipline == Discipline.FIFO:
                        n_id, n_arr = waiting_queue.pop(0)
                    else: # LIFO
                        n_id, n_arr = waiting_queue.pop()
                    st = self.next_service_time()
                    heapq.heappush(event_queue, Event(current_time + st, EventType.DEPARTURE, n_id, n_arr))
                else:
                    server_busy = False

        l_measured = area_n / current_time
        lambda_measured = completed_requests / current_time
        w_measured = total_residence_time / completed_requests
        l_little = lambda_measured * w_measured
        error_pct = abs(l_measured - l_little) / l_measured * 100.0

        return {
            "time": current_time,
            "completed": completed_requests,
            "L_measured": l_measured,
            "lambda_measured": lambda_measured,
            "W_measured": w_measured,
            "L_little": l_little,
            "error_pct": error_pct
        }

if __name__ == "__main__":
    tests = [
        ("Тест 1: M/M/1 черга з FIFO", 8.0, 10.0, Discipline.FIFO, False),
        ("Тест 2: M/M/1 черга з LIFO", 8.0, 10.0, Discipline.LIFO, False),
        ("Тест 3: M/G/1 з важкими хвостами", 5.0, 10.0, Discipline.FIFO, True),
    ]

    for name, lam, mu, disc, heavy in tests:
        sim = QueueSimulator(lam, mu, disc, heavy)
        res = sim.run(100000.0)
        print(f"=== {name} ===")
        print(f"Час: {res['time']:.1f} с, Завершено: {res['completed']}")
        print(f"L (виміряне)    : {res['L_measured']:.5f}")
        print(f"λ (виміряне)    : {res['lambda_measured']:.5f} req/s")
        print(f"W (виміряне)    : {res['W_measured']:.5f} s")
        print(f"λ · W           : {res['L_little']:.5f}")
        print(f"Похибка Літтла  : {res['error_pct']:.4f} %\n")
