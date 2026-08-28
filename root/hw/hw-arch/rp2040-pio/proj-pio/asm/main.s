; WS2812 — pioasm; clock divider → автомат на 20 МГц, 1 такт ≈ 50 нс
; один біт = 25 тактів ≈ 1.25 мкс
.program ws2812
.side_set 1              ; side-set керує 1 ніжкою (DATA) паралельно

.wrap_target
bitloop:
    out x, 1   side 0 [6]  ; зсунути 1 біт у X; ніжка LOW  (7 тактів = 350 нс)
    jmp !x, do0 side 1 [3] ; якщо X==0 → do0; ніжка HIGH, фронт вгору (+4 такти)
    jmp bitloop side 1 [11]; біт «1»: HIGH ще +12 тактів → T1H ≈ 800 нс
do0:
    jmp bitloop side 0 [7] ; біт «0»: LOW  +8 тактів   → T0H ≈ 400 нс
.wrap
