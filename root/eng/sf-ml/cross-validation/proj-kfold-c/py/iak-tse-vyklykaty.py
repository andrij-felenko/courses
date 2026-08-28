# --- Твоя частина: одна модель, дві функції під контракт модуля. ---

g_model = Model()          # стан однієї моделі (ваги тощо)
g_data: list[Sample] = []  # десь лежать самі приклади

# Навчити З НУЛЯ на прикладах, чиї індекси дав модуль.
# Ключове: обнулити модель на вході, бо той самий g_model
# використовується в наступному проході.
def train(idx: list[int], n: int) -> None:
    model_reset(g_model)                       # СКИНУТИ — інакше ваги накопичаться між проходами
    for i in range(n):
        model_update(g_model, g_data[idx[i]])  # учимо лише на цих прикладах

# Частка правильних на прикладах, чиї індекси дав модуль.
def accuracy(idx: list[int], n: int) -> float:
    correct = 0
    for i in range(n):
        pred = model_predict(g_model, g_data[idx[i]])
        if pred == g_data[idx[i]].label:
            correct += 1
    return correct / n

# --- Виклик: ---
def run_evaluation() -> None:
    r = cross_validate(200, 5, seed=42)
    print(f"точність: {r.mean * 100:.1f}% ± {r.sd * 100:.1f}%")
    # напр.: "точність: 86.0% ± 1.7%" — середнє й розкид по 5 проходах
