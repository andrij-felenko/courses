// Q-таблиця: [скільки станів][скільки дій]; тут S станів, A дій
float Q[S][A];

// одне оновлення Q-навчання після переходу s --a--> s' з винагородою r
void q_update(int s, int a, float r, int s_next,
              float alpha, float gamma)
{
    // 1) знайти найкраще Q у наступному стані (max по діях)
    float best_next = Q[s_next][0];
    for (int j = 1; j < A; ++j)
        if (Q[s_next][j] > best_next)
            best_next = Q[s_next][j];

    // 2) ціль за Беллманом: винагорода + знецінене найкраще продовження
    float target = r + gamma * best_next;   // 1 + 0.9*8 = 8.2

    // 3) несподіванка δ і крок до цілі
    float delta = target - Q[s][a];         // 8.2 - 4 = 4.2
    Q[s][a] += alpha * delta;               // 4 + 0.1*4.2 = 4.42
}
