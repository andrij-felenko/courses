"""
breadboard_parasitics.py
Фізико-математичне моделювання вимірювального стенда та обчислення
еквівалентних паразитних R і C параметрів безпаяльної макетної плати.

Реалізує розрахунок міжрейкової паразитної ємності з компенсацією власної ємності
осцилографічного щупа, розрахунок контактного опору пружинних затискачів за величиною
спаду напруги під імпульсним струмом навантаження, визначення граничної частоти зрізу
RC-ланцюга та автоматичну класифікацію технічного стану контактів.
"""
from dataclasses import dataclass
from enum import Enum
import math
from typing import Optional, Union

from oscilloscope_trace import OscilloscopeTrace, LN_9

TWO_PI: float = 2.0 * math.pi


class ContactHealth(str, Enum):
    """
    Класифікація технічного стану контактних затискачів макетної плати.
    """
    NEW = "новий"                 # Новий контакт (відмінний стан, R_cont < 50 мОм)
    ACCEPTABLE = "задовільний"   # Задовільний робочий стан (50 мОм <= R_cont <= 200 мОм)
    DEGRADED = "деградований"     # Зношений або окислений контакт (R_cont > 200 мОм)

    def describe(self) -> str:
        """Повертає людиночитаний опис технічного стану."""
        if self == ContactHealth.NEW:
            return "Новий (відмінний)"
        if self == ContactHealth.ACCEPTABLE:
            return "Задовільний"
        return "Зношений / окислений"


@dataclass(frozen=True)
class TestBenchConfig:
    """
    Параметри конфігурації вимірювального стенда.

    Атрибути:
        test_resistance_ohm: Опір тестового резистора R_test (Ом). Типово 10 кОм.
        probe_capacitance_f: Власна ємність щупа осцилографа C_probe (Ф). Типово 12 пФ для 10X.
        test_load_current_a: Тестовий струм навантаження I_test (А). Типово 0.5 А.
    """
    test_resistance_ohm: float = 10_000.0
    probe_capacitance_f: float = 12.0e-12
    test_load_current_a: float = 0.5

    def __post_init__(self) -> None:
        if self.test_resistance_ohm <= 0.0:
            raise ValueError("Опір тестового резистора повинен бути суворо додатним.")
        if self.probe_capacitance_f < 0.0:
            raise ValueError("Власна ємність щупа не може бути від'ємною.")
        if self.test_load_current_a <= 0.0:
            raise ValueError("Тестовий струм навантаження повинен бути суворо додатним.")


@dataclass(frozen=True)
class ParasiticReport:
    """
    Зведений метрологічний та діагностичний звіт параметрів контакту макетної плати.

    Атрибути:
        rise_time_ns: Тривалість наростання фронту t_r (10%-90%) у наносекундах.
        tau_ns: Розрахована постійна часу RC-перехідного процесу τ у наносекундах.
        total_capacitance_pf: Повна виміряна ємність вимірювального вузла C_total у пікофарадах.
        parasitic_capacitance_pf: Власна міжрейкова паразитна ємність плати C_par у пікофарадах.
        cutoff_frequency_mhz: Гранична частота зрізу f_-3dB на тестовому опорі в мегагерцах.
        voltage_drop_mv: Резистивне падіння напруги на контакті під навантаженням у мілівольтах.
        contact_resistance_mohm: Розрахований контактний опір затискача R_cont у міліомах.
        health: Класифікація технічного стану контактної групи.
        notes: Інженерний вердикт та експлуатаційні рекомендації для макетування.
    """
    rise_time_ns: float
    tau_ns: float
    total_capacitance_pf: float
    parasitic_capacitance_pf: float
    cutoff_frequency_mhz: float
    voltage_drop_mv: float
    contact_resistance_mohm: float
    health: ContactHealth
    notes: str


class BreadboardParasiticsAnalyzer:
    """
    Обчислювальний аналізатор паразитних компонентів безпаяльної макетної плати.

    Визначає міжрейкову паразитну ємність за часом наростання перехідного процесу
    з компенсацією власної ємності вимірювального щупа, розраховує контактний опір
    за просіданням напруги під навантаженням та оцінює граничну частоту сигналів.
    """

    def __init__(self, config: Optional[TestBenchConfig] = None) -> None:
        self.config: TestBenchConfig = config if config is not None else TestBenchConfig()

    def calculate_total_capacitance(self, rise_time_s: float) -> float:
        """
        Розрахунок повної еквівалентної ємності вузла:
        C_total = t_r / (ln(9) * R_test) = tau / R_test
        """
        if rise_time_s <= 0.0:
            return 0.0
        return rise_time_s / (LN_9 * self.config.test_resistance_ohm)

    def calculate_parasitic_capacitance(self, rise_time_s: float) -> float:
        """
        Розрахунок чистої паразитної ємності макетної плати з компенсацією щупа:
        C_par = max(0, C_total - C_probe)
        """
        c_total = self.calculate_total_capacitance(rise_time_s)
        return max(0.0, c_total - self.config.probe_capacitance_f)

    def calculate_contact_resistance(self, voltage_drop_v: float) -> float:
        """
        Розрахунок контактного опору пружинного затискача:
        R_cont = Delta_V / I_load
        """
        if voltage_drop_v <= 0.0 or self.config.test_load_current_a <= 0.0:
            return 0.0
        return voltage_drop_v / self.config.test_load_current_a

    def calculate_cutoff_frequency(self, capacitance_f: float) -> float:
        """
        Розрахунок частоти зрізу f_-3dB еквівалентного фільтра низьких частот:
        f_-3dB = 1 / (2 * pi * R_test * C_par)
        """
        if capacitance_f <= 1.0e-15 or self.config.test_resistance_ohm <= 0.0:
            return 0.0
        return 1.0 / (TWO_PI * self.config.test_resistance_ohm * capacitance_f)

    def assess_contact_health(self, contact_resistance_ohm: float) -> ContactHealth:
        """
        Автоматична класифікація технічного стану контакту:
        - < 50 мОм: новий якісний пружинний контакт із фосфористої бронзи;
        - 50..200 мОм: допустимий робочий стан (помірне окиснення);
        - > 200 мОм: деградований контакт (втома металу затискача, сильне окиснення).
        """
        if contact_resistance_ohm < 0.050:
            return ContactHealth.NEW
        if contact_resistance_ohm <= 0.200:
            return ContactHealth.ACCEPTABLE
        return ContactHealth.DEGRADED

    def extract_contact_voltage_drop(self, load_trace: OscilloscopeTrace) -> float:
        """
        Виділення величини спаду напруги з осцилограми імпульсного навантаження.
        Визначає різницю між напругою холостого ходу (V_idle) та мінімальною
        напругою під час дії тестового струму (V_min).
        """
        samples = load_trace.samples
        if len(samples) < 4:
            return 0.0

        init_count = max(2, len(samples) // 10)
        v_idle = sum(samples[i].voltage_v for i in range(init_count)) / init_count
        v_min = min(s.voltage_v for s in samples)
        return max(0.0, v_idle - v_min)

    def analyze(
        self,
        step_trace: OscilloscopeTrace,
        load_data: Union[float, OscilloscopeTrace],
    ) -> ParasiticReport:
        """
        Комплексний аналіз паразитної ємності та контактного опору.

        Параметри:
            step_trace: Осцилограма перехідного процесу заряджання ємності (RC-фронт).
            load_data: Або числове значення спаду напруги (у вольтах), або осцилограма
                       імпульсу навантаження для автоматичного виділення спаду.
        """
        # 1. Аналіз динаміки наростання сигналу
        tr_s = step_trace.calculate_rise_time(0.10, 0.90) or 0.0
        tau_s = tr_s / LN_9 if tr_s > 0.0 else 0.0

        # 2. Розрахунок ємнісних параметрів та частоти зрізу
        c_tot_f = self.calculate_total_capacitance(tr_s)
        c_par_f = self.calculate_parasitic_capacitance(tr_s)
        f_cutoff_hz = self.calculate_cutoff_frequency(c_par_f)

        # 3. Визначення контактного опору
        if isinstance(load_data, OscilloscopeTrace):
            drop_v = self.extract_contact_voltage_drop(load_data)
        else:
            drop_v = max(0.0, float(load_data))

        r_cont_ohm = self.calculate_contact_resistance(drop_v)
        health = self.assess_contact_health(r_cont_ohm)

        c_par_pf = c_par_f * 1.0e12
        r_cont_mohm = r_cont_ohm * 1.0e3

        # 4. Формування інженерних висновків
        notes_parts = [f"Стан контактної групи: {health.describe()}."]
        if health == ContactHealth.NEW:
            notes_parts.append(
                "Низький опір контакту (<50 мОм), придатний для живлення з імпульсним струмом до 1 А."
            )
        elif health == ContactHealth.ACCEPTABLE:
            notes_parts.append(
                "Опір у межах робочої норми. Рекомендовано обмежити тривалий струм до 0.5 А."
            )
        else:
            notes_parts.append(
                "УВАГА: контакт деградований (>200 мОм)! Ризик просідання живлення VCC та локального нагріву."
            )

        if c_par_pf <= 3.0:
            notes_parts.append(
                f"Паразитна ємність рейок у типових межах ({c_par_pf:.1f} пФ). "
                "Макет придатний для інтерфейсів I2C (до 400 кГц) та швидких логічних сигналів."
            )
        else:
            notes_parts.append(
                f"Підвищена міжрейкова ємність ({c_par_pf:.1f} пФ). "
                "Можливі завали фронтів імпульсів та ємнісні перехресні завади (crosstalk)."
            )

        return ParasiticReport(
            rise_time_ns=tr_s * 1.0e9,
            tau_ns=tau_s * 1.0e9,
            total_capacitance_pf=c_tot_f * 1.0e12,
            parasitic_capacitance_pf=c_par_pf,
            cutoff_frequency_mhz=f_cutoff_hz / 1.0e6,
            voltage_drop_mv=drop_v * 1.0e3,
            contact_resistance_mohm=r_cont_mohm,
            health=health,
            notes=" ".join(notes_parts),
        )
