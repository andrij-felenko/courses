import numpy as np

# Середньоквадратична похибка для масиву прогнозів
def mse(pred, truth):
    e = np.asarray(pred) - np.asarray(truth)   # помилка зі знаком
    return np.mean(e * e)                        # квадрат прибирає знак і роздуває великі

# e   = [-0.4,  2.0, -0.3]
# e²  = [ 0.16, 4.00, 0.09]
# сума = 4.25  →  MSE = 4.25 / 3 ≈ 1.42
