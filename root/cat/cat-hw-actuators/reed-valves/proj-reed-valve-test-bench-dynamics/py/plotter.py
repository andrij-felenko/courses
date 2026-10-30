class ResponsePlotter:
    def __init__(self, time_data: list, pressure_data: list, flow_data: list):
        self.time_data = time_data
        self.pressure_data = pressure_data
        self.flow_data = flow_data

    def save_plot(self, filename: str):
        # Оскільки в мінімальному середовищі matplotlib може бути відсутній або не потрібен для базового прикладу,
        # реалізуємо текстове збереження або базовий вивід, або мінімальний matplotlib код з обробкою винятків.
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 5))
            plt.plot(self.time_data, self.pressure_data, label="Тиск (kPa)")
            plt.plot(self.time_data, self.flow_data, label="Потік (ml/s)")
            plt.xlabel("Час (с)")
            plt.ylabel("Значення")
            plt.title("Динамічна характеристика пелюсткового клапана")
            plt.legend()
            plt.grid(True)
            plt.savefig(filename)
            plt.close()
        except ImportError:
            # Якщо matplotlib недоступний, записуємо текстовий звіт замість картинки
            with open(filename, "w", encoding="utf-8") as f:
                f.write("Mock plot data: Time, Pressure, Flow\n")
                for t, p, fl in zip(self.time_data[::50], self.pressure_data[::50], self.flow_data[::50]):
                    f.write(f"{t:.4f}, {p:.2f}, {fl:.2f}\n")
