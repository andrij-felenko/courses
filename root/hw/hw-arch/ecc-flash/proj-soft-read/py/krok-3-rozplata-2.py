RBER, N, M = 0.05, 5, 2_000_000
sigma, rber_emp, edges, table, w_hard, w_quant, w_full, hard_an, soft_an = simulate(RBER, N, M)

print(f"σ = {sigma:.4f}    емпіричний RBER (голі біти) = {rber_emp:.4f}")
for name, v in [("глибоко в рівні 0    ", MU0), ("майже на межі (0-бік)", -0.05),
                ("майже на межі (1-бік)", +0.05), ("глибоко в рівні 1    ", MU1)]:
    print(f"  {name}  Vth = {v:+.2f}   LLR = {llr_full(v, sigma):+.2f}")
print("  межі read-retry:", "  ".join(f"{e:+.3f}" for e in edges))
print("  LLR смуг:       ", "  ".join(f"{t:+.2f}" for t in table))
print(f"  ТВЕРДЕ  більшість голосів : WER = {w_hard:.2e}   (аналітично {hard_an:.2e})")
print(f"  М'ЯКЕ   квантоване (5 чит.): WER = {w_quant:.2e}")
print(f"  М'ЯКЕ   повна роздільність : WER = {w_full:.2e}   (аналітично {soft_an:.2e})")
print(f"  виграш тверде / м'яке ≈ {w_hard/w_full:.0f}×")
