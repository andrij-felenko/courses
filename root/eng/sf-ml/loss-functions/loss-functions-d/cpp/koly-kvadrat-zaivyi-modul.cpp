// Втрата Губера: квадрат для малих помилок, модуль — для великих
float huber(float pred, float truth, float delta) {
    float e = pred - truth;
    float a = fabsf(e);
    if (a <= delta)
        return 0.5f * e * e;                 // гладка квадратична серцевина
    else
        return delta * (a - 0.5f * delta);   // лінійні «хвости» проти викидів
}
// малий промах e=0.4, δ=1 → 0.5·0.16 = 0.08 (як MSE)
// викид     e=10,  δ=1 → 1·(10 − 0.5) = 9.5 (як MAE, а не 100!)
