from enum import Enum


class TrackState(Enum):
    TENTATIVE = 0
    CONFIRMED = 1
    DELETED = 2


class Track:
    def __init__(self, track_id, kf):
        self.id = track_id          # стійкий номер об'єкта
        self.kf = kf                # фільтр Калмана зі станом цілі
        self.state = TrackState.TENTATIVE
        self.hits = 0               # скільки разів поспіль був збіг
        self.misses = 0             # скільки кадрів поспіль без детекції
        self.age = 0                # скільки кадрів живе всього


def update_tracks(tracks, dets, matched, min_hits, max_missed):
    """Один кадр: tracks[] уже мають прогноз (predict зроблено),
    matched[i] = індекс детекції для треку i або -1 (без пари)."""
    for i, t in enumerate(tracks):
        t.age += 1

        if matched[i] >= 0:                       # є детекція → update фільтра
            t.kf.update(dets[matched[i]])
            t.hits += 1
            t.misses = 0
            if t.state is TrackState.TENTATIVE and t.hits >= min_hits:
                t.state = TrackState.CONFIRMED    # проба витримала → підтверджено
        else:                                      # пари немає → ведемо наосліп
            t.misses += 1
            if t.state is TrackState.TENTATIVE:
                t.state = TrackState.DELETED      # проба зірвалась одразу
            elif t.misses > max_missed:
                t.state = TrackState.DELETED      # підтверджений жив, та зник надовго

    # (окремим проходом: викинути DELETED і завести нові TENTATIVE
    #  з детекцій, що лишились без пари — див. тему sort-tracking-algorithm)
