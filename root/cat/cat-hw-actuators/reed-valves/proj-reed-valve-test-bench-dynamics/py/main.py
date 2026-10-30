import time
from visa_client import VisaReader
from analyzer import ValveAnalyzer
from plotter import ResponsePlotter

def main():
    print("Ініціалізація вимірювального комплексу пелюсткових клапанів мікрогідравліки...")
    
    # Підключення до приладу через VISA (наприклад, осцилограф/генератор)
    visa_address = "TCPIP0::192.168.1.100::INSTR"
    reader = VisaReader(visa_address)
    
    try:
        reader.connect()
        print(логування := f"З'єднання встановлено з {visa_address}")
        
        # Налаштування параметрів вимірювання частоти (10 Гц - 1 кГц)
        frequency = 100.0 # Гц
        print(f"Запуск вимірювання на частоті {frequency} Гц...")
        
        # Зчитування сирих масивів даних (сигнал тиску та потоку/струму)
        time_data, pressure_data, flow_data = reader.read_waveforms()
        
        # Аналіз характеристик
        analyzer = ValveAnalyzer(time_data, pressure_data, flow_data)
        phase_shift = analyzer.detect_phase_shift()
        reverse_flow = analyzer.calculate_dynamic_reverse_flow()
        
        print(f"Виявлений фазовий зсув: {phase_shift:.2f} град.")
        print(f"Динамічний зворотний потік: {reverse_flow:.4f} мл/с")
        
        # Побудова та збереження графіків
        plotter = ResponsePlotter(time_data, pressure_data, flow_data)
        plotter.save_plot("valve_response.png")
        print("Графік успішно збережено у файл valve_response.png")
        
    except Exception as e:
        print(f"Помилка під час виконання вимірювального циклу: {e}")
    finally:
        reader.disconnect()
        print("З'єднання закрито.")

if __name__ == "__main__":
    main()
