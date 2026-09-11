import numpy as np
import pytest

# Перелік підсистем Digital Homes
COMPONENTS = [
    "SecurityCore",      # v1: ядро безпеки (квартальний реліз)
    "DeviceStorage",     # v2: спільне сховище конфігурації
    "SensorTelemetry",   # v3: збір метрик сенсорів
    "CloudGateway",      # v4: інтеграційний хмарний шлюз
    "MobileUI",          # v5: мобільний користувацький інтерфейс
]

def load_tempo_vector() -> np.ndarray:
    """
    Емуляція вивантаження частоти змін (комітів на місяць) за останні 90 днів.
    У реальному CI дані витягуються через 'git log --since=90.days.ago'.
    """
    return np.array([0.33, 1.00, 2.00, 4.00, 8.00])

def build_dsm_matrix() -> np.ndarray:
    """
    Побудова бінарної матриці залежностей A за результатами статичного аналізу коду.
    Рядок i залежить від стовпця j (A[i, j] = 1).
    """
    n = len(COMPONENTS)
    A = np.zeros((n, n), dtype=int)
    
    # Ребра поточної архітектури
    A[2, 1] = 1  # SensorTelemetry -> DeviceStorage
    A[3, 1] = 1  # CloudGateway -> DeviceStorage
    A[4, 1] = 1  # MobileUI -> DeviceStorage
    A[4, 3] = 1  # MobileUI -> CloudGateway
    
    # Симуляція небезпечного PR: розробник додав прямий виклик DeviceStorage у SecurityCore!
    # A[0, 1] = 1 # v1 (SecurityCore) -> v2 (DeviceStorage)
    
    return A

def build_propagation_matrix(A: np.ndarray) -> np.ndarray:
    """
    Формування матриці ймовірностей передачі збурень P на основі зв'язності.
    """
    P = np.zeros_like(A, dtype=float)
    # Калібровані ймовірності для активних ребер
    if A[0, 1] == 1:
        P[0, 1] = 0.80  # Ядро вкрай чутливе до змін сховища
    if A[2, 1] == 1:
        P[2, 1] = 0.50
    if A[3, 1] == 1:
        P[3, 1] = 0.60
    if A[4, 1] == 1:
        P[4, 1] = 0.70
    if A[4, 3] == 1:
        P[4, 3] = 0.50
    return P

def test_tempo_gradient_fitness():
    """
    Фітнес-функція 1: перевірка принципу стабільності за темпом (монотонності).
    PR відхиляється, якщо будь-яка вихідна залежність веде до швидшого модуля.
    """
    tau = load_tempo_vector()
    A = build_dsm_matrix()
    n = len(COMPONENTS)
    
    inversions = []
    total_omega = 0.0
    
    for i in range(n):
        for j in range(n):
            if A[i, j] == 1:
                delta_tau = tau[i] - tau[j]
                if delta_tau < 0:
                    penalty = tau[j] - tau[i]
                    total_omega += penalty
                    inversions.append(
                        f"Інверсія: '{COMPONENTS[i]}' (τ={tau[i]}) спирається на "
                        f"швидший '{COMPONENTS[j]}' (τ={tau[j]}), перепад Δτ = {delta_tau:.2f}"
                    )
    
    # Вимогливий поріг: індекс інверсії має дорівнювати 0.00
    assert total_omega == 0.0, (
        f"CI заблокував PR! Виявлено інверсію темпів (загальна Ω = {total_omega:.2f}):\n"
        + "\n".join(inversions)
    )

def test_blast_radius_fitness():
    """
    Фітнес-функція 2: контроль транзитивного радіуса ураження ядра через (I - P)^(-1).
    PR відхиляється, якщо спектральний радіус rho(P) >= 1 або чутливість ядра перевищує 0.1.
    """
    A = build_dsm_matrix()
    P = build_propagation_matrix(A)
    n = len(COMPONENTS)
    
    # 1. Перевірка спектрального радіуса (відсутність циклічного резонансу)
    eigenvalues = np.linalg.eigvals(P)
    spectral_radius = float(np.max(np.abs(eigenvalues)))
    assert spectral_radius < 1.0, (
        f"CI заблокував PR! Спектральний радіус ρ(P) = {spectral_radius:.2f} >= 1.0. "
        "У системі присутній небезпечний цикл залежностей!"
    )
    
    # 2. Обчислення транзитивного замикання за рядом Неймана: R = (I - P)^(-1) - I
    I = np.eye(n)
    inv_matrix = np.linalg.inv(I - P)
    R = inv_matrix - I
    
    # Чутливість ядра безпеки SecurityCore (індекс 0) до зовнішніх правок: сума рядка 0
    security_sensitivity = float(np.sum(R[0, :]))
    MAX_CORE_SENSITIVITY = 0.10
    
    assert security_sensitivity <= MAX_CORE_SENSITIVITY, (
        f"CI заблокував PR! Чутливість SecurityCore до чужих правок становить "
        f"{security_sensitivity:.2f}, що перевищує допустимий ліміт {MAX_CORE_SENSITIVITY}. "
        "Ядро захисту не може бути піддане каскадним ризикам зовнішніх сервісів."
    )
