import math

def calculate_http_replicas(current_replicas: int,
                           current_metric: float,
                           target_metric: float,
                           tolerance: float,
                           min_rep: int,
                           max_rep: int) -> int:
    ratio = current_metric / target_metric
    if abs(ratio - 1.0) <= tolerance:
        return current_replicas
    desired = math.ceil(current_replicas * ratio)
    return max(min_rep, min(desired, max_rep))


def calculate_queue_workers(queue_lag: int,
                            arrival_rate_rps: float,
                            task_duration_sec: float,
                            target_drain_time_sec: float,
                            max_workers: int) -> int:
    if queue_lag <= 0 and arrival_rate_rps <= 0.0:
        return 0
    total_tasks = queue_lag + arrival_rate_rps * target_drain_time_sec
    tasks_per_worker = target_drain_time_sec / task_duration_sec
    desired = math.ceil(total_tasks / tasks_per_worker)
    return min(desired, max_workers)


if __name__ == "__main__":
    http_pool = calculate_http_replicas(8, 88.0, 65.0, 0.10, 4, 20)
    worker_pool = calculate_queue_workers(45000, 250.0, 0.12, 60.0, 200)

    print(f"HTTP API target replicas: {http_pool} (очікується 11)")
    print(f"Queue Workers target pool: {worker_pool} (очікується 120)")
