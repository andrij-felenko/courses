#!/usr/bin/env python3
"""Проганяє стенд R разів і звіряє вимір з аналітичним очікуванням."""
import math, statistics, subprocess

RUNS, P, L = 2000, 1e-6, 1024

out = subprocess.run(["./stand", "--runs", str(RUNS), repr(P)],
                     capture_output=True, text=True, check=True).stdout
xs = [int(v) for v in out.split()]

mean, sd = statistics.fmean(xs), statistics.stdev(xs)
se = sd / math.sqrt(len(xs))

p_parity = (L // 2) ** 2 * 2 / (L * (L - 1))     # зсуви різної парності
p_real = 255 / 256                               # байти в парі різні
p_miss = 1 / 3 + 2 / 3 * (1 - p_parity)          # ділянкова перевірка сліпа
q = 3 * P * p_real * p_miss

print(f"прогонів      {len(xs):>12,}")
print(f"середнє       {mean:>12,.0f}   теорія 1/q = {1 / q:,.0f}")
print(f"95 % смуга    {mean - 1.96 * se:>12,.0f} .. {mean + 1.96 * se:,.0f}")
print(f"σ             {sd:>12,.0f}   (у геометричного σ ≈ середнє)")
print(f"медіана       {statistics.median(xs):>12,.0f}   теорія ln2/q = {math.log(2) / q:,.0f}")
print(f"найкоротший   {min(xs):>12,}")
print(f"найдовший     {max(xs):>12,}")
