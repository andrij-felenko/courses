#!/usr/bin/env python3
"""Аналізатор спектральних піків та гармонійних сіток для CSV-дампів SDR/TinySA."""
import csv
import sys
import math

KNOWN_SOURCES = [
    {"name": "DCDC Switcher (Buck)", "fund_freq": 1.2e6, "tolerance": 25e3},
    {"name": "Кварц MCU (HSE)", "fund_freq": 25.0e6, "tolerance": 50e3},
    {"name": "USB 2.0 PHY Clock", "fund_freq": 48.0e6, "tolerance": 80e3},
    {"name": "SPI Flash Bus", "fund_freq": 80.0e6, "tolerance": 150e3},
]

def analyze_spectrum(csv_path, threshold_delta_db=10.0, window=8):
    frequencies = []
    powers = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            try:
                frequencies.append(float(row[0]))
                powers.append(float(row[1]))
            except ValueError:
                continue

    n = len(frequencies)
    peaks = []

    for i in range(window, n - window):
        # Локальний максимум
        if powers[i] <= powers[i - 1] or powers[i] <= powers[i + 1]:
            continue

        # Підлога шуму навколо піку
        window_powers = [powers[i + w] for w in range(-window, window + 1) if abs(w) > 1]
        noise_floor = sum(window_powers) / len(window_powers)
        delta = powers[i] - noise_floor

        if delta >= threshold_delta_db:
            freq = frequencies[i]
            matched_src = "Невідоме джерело"
            harmonic_num = 0

            for src in KNOWN_SOURCES:
                ratio = freq / src["fund_freq"]
                order = round(ratio)
                if order >= 1 and abs(freq - order * src["fund_freq"]) <= src["tolerance"]:
                    matched_src = src["name"]
                    harmonic_num = order
                    break

            peaks.append({
                "freq_mhz": freq / 1e6,
                "power_dbm": powers[i],
                "delta_db": delta,
                "source": matched_src,
                "harmonic": harmonic_num
            })

    print(f"Знайдено небезпечних піків: {len(peaks)}")
    print(f"{'Частота (МГц)':<15} {'Рівень (дБм)':<14} {'Дельта (дБ)':<12} {'Джерело випромінювання':<25} {'Гармоніка'}")
    print("-" * 75)
    for p in peaks:
        h_str = f"H{p['harmonic']}" if p['harmonic'] > 0 else "-"
        print(f"{p['freq_mhz']:<15.3f} {p['power_dbm']:<14.1f} {p['delta_db']:<12.1f} {p['source']:<25} {h_str}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_spectrum(sys.argv[1])
    else:
        print("Використання: python emc_peak_hunter.py <spectrum_data.csv>")
