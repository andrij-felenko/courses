from statistics import median


def theil_sen_velocity(ts, xs):
    """Стійка оцінка: медіана нахилів усіх пар точок (Тейл–Сен).
       Витримує до ~29 % викидів. O(n²) пар — дешево для вікна в 5–15 відліків."""
    slopes = [(xs[j] - xs[i]) / (ts[j] - ts[i])
              for i in range(len(ts))
              for j in range(i + 1, len(ts))
              if ts[j] != ts[i]]
    return median(slopes)
