# -*- coding: utf-8 -*-
"""Емуляція роботи гібридного ABR-рушія на динамічному мережевому трасі."""

class AbrSimulator:
    def __init__(self, profiles, segment_duration=4.0):
        self.profiles = sorted(profiles)
        self.seg_dur = segment_duration
        self.buffer = 0.0
        self.history = []
        self.smoothed_tp = profiles[0]
        self.current_idx = 0
        self.in_startup = True
        self.reservoir = 8.0
        self.cushion = 16.0

    def add_telemetry(self, bytes_transferred, duration_sec):
        inst_tp = (bytes_transferred * 8.0) / duration_sec
        self.history.append((bytes_transferred, duration_sec))
        if len(self.history) > 5:
            self.history.pop(0)

        # Гармонійне середнє за 5 чанками
        tot_bytes = sum(h[0] for h in self.history)
        tot_time = sum(h[1] for h in self.history)
        harm_tp = (tot_bytes * 8.0) / tot_time

        # EWMA
        self.smoothed_tp = 0.85 * harm_tp + 0.15 * self.smoothed_tp

    def decide_next_chunk(self):
        # Startup
        if self.in_startup:
            if self.buffer >= (self.reservoir + self.cushion * 0.5):
                self.in_startup = False
            else:
                safe_tp = self.smoothed_tp * 0.75
                best = 0
                for i, r in enumerate(self.profiles):
                    if r <= safe_tp:
                        best = i
                self.current_idx = best
                return best

        # BBA
        if self.buffer <= self.reservoir:
            target = self.profiles[0]
        elif self.buffer >= (self.reservoir + self.cushion):
            target = self.profiles[-1]
        else:
            factor = (self.buffer - self.reservoir) / self.cushion
            target = self.profiles[0] + factor * (self.profiles[-1] - self.profiles[0])

        # Clamp & Hysteresis
        target = min(target, self.smoothed_tp * 0.85)
        cand = 0
        for i, r in enumerate(self.profiles):
            if r <= target:
                cand = i

        if cand > self.current_idx + 1:
            cand = self.current_idx + 1

        self.current_idx = cand
        return cand

    def run_simulation(self, network_trace_mbps):
        print(f"{'Чанк':>5} | {'Мережа [Мб/с]':>14} | {'Обрано [Мб/с]':>14} | {'Буфер [с]':>10} | {'Пауза [с]':>10}")
        print("-" * 65)

        total_stall = 0.0
        for k, net_mbps in enumerate(network_trace_mbps):
            profile_idx = self.decide_next_chunk()
            bitrate_bps = self.profiles[profile_idx]
            chunk_bits = bitrate_bps * self.seg_dur
            net_bps = net_mbps * 1e6

            # Час завантаження
            t_dl = chunk_bits / net_bps
            bytes_sent = chunk_bits / 8.0
            self.add_telemetry(bytes_sent, t_dl)

            # Оновлення буфера
            stall = max(0.0, t_dl - self.buffer)
            total_stall += stall
            self.buffer = max(0.0, self.buffer - t_dl) + self.seg_dur

            print(f"{k+1:5d} | {net_mbps:14.2f} | {bitrate_bps/1e6:14.2f} | {self.buffer:10.2f} | {stall:10.2f}")

        print("-" * 65)
        print(f"Сумарний час зависання (Rebuffering): {total_stall:.2f} с")


if __name__ == "__main__":
    bitrate_ladder = [800000, 1600000, 3200000, 6000000] # 0.8, 1.6, 3.2, 6.0 Мбіт/с
    trace = [10.0] * 15 + [1.2] * 15 + [8.0] * 15         # 45 сегментів
    sim = AbrSimulator(bitrate_ladder)
    sim.run_simulation(trace)
