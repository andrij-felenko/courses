"""
Модуль чисельного моделювання динаміки шини постійного струму (DC bus)
сервопривода під час рекуперативного гальмування.

Імітує роботу апаратного гістерезисного компаратора, перемикання баластного MOSFET
та інтегрує баланс струмів конденсаторів шини за диференціальним рівнянням:
    C_bus * (dV_bus / dt) = I_supply + I_regen - I_brake - I_quiescent
"""

from dataclasses import dataclass, field
import math
from typing import Callable, List, Optional


class HysteresisComparator:
    """
    Модель апаратного компаратора з гістерезисом (тригера Шмітта).
    
    Формує керуючий бінарний сигнал увімкнення/вимкнення силового ключа
    за поточною напругою шини DC та встановленими порогами V_on і V_off.
    """

    def __init__(self, v_on: float, v_off: float, initial_state: bool = False):
        if v_off >= v_on:
            raise ValueError(f"Поріг V_off ({v_off}V) повинен бути меншим за V_on ({v_on}V).")
        self.v_on = float(v_on)
        self.v_off = float(v_off)
        self._state = bool(initial_state)
        self._switch_count = 0

    @property
    def state(self) -> bool:
        """Поточний логічний стан виходу компаратора (True = ключ замкнено)."""
        return self._state

    @property
    def switch_count(self) -> int:
        """Кількість комутаційних перемикань компаратора."""
        return self._switch_count

    def update(self, v_in: float) -> bool:
        """
        Оновлює стан компаратора відповідно до вхідної напруги v_in.
        
        :param v_in: Поточна напруга на шині DC, В.
        :return: Логічний стан виходу компаратора (True = ON, False = OFF).
        """
        if not self._state:
            # Стан OFF: вмикання при досягненні верхнього порогу Von
            if v_in >= self.v_on:
                self._state = True
                self._switch_count += 1
        else:
            # Стан ON: вимикання при зниженні напруги до нижнього порогу Voff
            if v_in <= self.v_off:
                self._state = False
                self._switch_count += 1

        return self._state

    def reset(self, initial_state: bool = False) -> None:
        """Скидає внутрішній стан компаратора та лічильник комутацій."""
        self._state = bool(initial_state)
        self._switch_count = 0


@dataclass
class SimulationResult:
    """Підсумкові метрики та дискретизовані часові ряди моделювання."""
    duration: float                      # Тривалість симуляції, с
    v_max: float                         # Максимальна зафіксована напруга шини DC, В
    v_min: float                         # Мінімальна зафіксована напруга шини DC, В
    v_final: float                       # Кінцева напруга шини DC після завершення симуляції, В
    e_regen_total: float                 # Сумарна рекуперована енергія, Дж
    e_brake_dissipated: float            # Повна енергія, розсіяна баластним резистором, Дж
    chopper_active_time: float           # Сумарний час відкритого стану баластного ключа, с
    chopper_duty_cycle: float            # Відносний час роботи чопера під час гальмування, %
    switch_count: int                    # Кількість комутацій силового ключа
    overvoltage_fault: bool              # Прапорець аварійного перевищення допустимої напруги

    # Дискретизовані масиви для візуалізації
    time_series: List[float] = field(default_factory=list)
    v_bus_series: List[float] = field(default_factory=list)
    i_regen_series: List[float] = field(default_factory=list)
    i_brake_series: List[float] = field(default_factory=list)
    chopper_state_series: List[bool] = field(default_factory=list)


class DcBusSimulator:
    """
    Чисельний симулятор перехідних процесів шини живлення постійного струму
    (DC bus) безколекторного сервопривода під час рекуперативного гальмування.
    """

    def __init__(
        self,
        c_bus: float,
        r_brake: float,
        v_nominal: float,
        v_on: float,
        v_off: float,
        v_max_safe: float = 60.0,
        r_source: float = 0.05,
        i_quiescent: float = 0.05,
    ):
        """
        :param c_bus: Ємність конденсаторів шини DC, Ф.
        :param r_brake: Опір баластного резистора, Ом.
        :param v_nominal: Номінальна напруга джерела живлення, В.
        :param v_on: Поріг увімкнення чопера, В.
        :param v_off: Поріг вимкнення чопера, В.
        :param v_max_safe: Гранично допустима безпечна напруга компонентів інвертора, В.
        :param r_source: Внутрішній імпеданс лінії та джерела живлення, Ом.
        :param i_quiescent: Струм холостого споживання електроніки сервоконтролера, А.
        """
        self.c_bus = float(c_bus)
        self.r_brake = float(r_brake)
        self.v_nominal = float(v_nominal)
        self.v_max_safe = float(v_max_safe)
        self.r_source = float(r_source)
        self.i_quiescent = float(i_quiescent)

        self.comparator = HysteresisComparator(v_on=v_on, v_off=v_off)

    def simulate(
        self,
        t_decel: float,
        p_regen_profile: Callable[[float], float],
        dt: float = 1e-5,
        t_total: Optional[float] = None,
        enable_chopper: bool = True,
        record_decimation: int = 20,
    ) -> SimulationResult:
        """
        Виконує чисельне моделювання динаміки напруги шини.
        
        :param t_decel: Тривалість активної фази гальмування приводу, с.
        :param p_regen_profile: Функція залежності рекуперативної потужності від часу t, Вт.
        :param dt: Крок інтегрування, с.
        :param t_total: Повний час інтервалу спостереження, с.
        :param enable_chopper: Увімкнення баластного чопера (False для виявлення перенапруги).
        :param record_decimation: Проріджування збереження точок траєкторії.
        :return: SimulationResult з результатами та графіками.
        """
        if t_total is None:
            t_total = t_decel * 1.6

        self.comparator.reset()

        v_bus = self.v_nominal
        v_max = v_bus
        v_min = v_bus
        overvoltage_fault = False

        e_regen_accum = 0.0
        e_brake_accum = 0.0
        chopper_on_time = 0.0

        time_series: List[float] = []
        v_bus_series: List[float] = []
        i_regen_series: List[float] = []
        i_brake_series: List[float] = []
        chopper_state_series: List[bool] = []

        total_steps = int(math.ceil(t_total / dt))

        for step in range(total_steps):
            t = step * dt

            # 1. Рекуперативна електрична потужність та струм інвертора
            p_regen = p_regen_profile(t) if t <= t_decel else 0.0
            i_regen = (p_regen / v_bus) if v_bus > 1.0 else 0.0

            # 2. Логіка компаратора та стан баластного ключа
            if enable_chopper:
                chopper_active = self.comparator.update(v_bus)
                i_brake = (v_bus / self.r_brake) if chopper_active else 0.0
            else:
                chopper_active = False
                i_brake = 0.0

            if chopper_active:
                chopper_on_time += dt

            # 3. Струм зовнішнього джерела живлення:
            # Діод блокує надходження зворотного рекуперативного струму в БЖ.
            # БЖ живить систему тільки тоді, коли V_bus опускається нижче V_nominal.
            if v_bus < self.v_nominal:
                i_supply = (self.v_nominal - v_bus) / self.r_source
            else:
                i_supply = 0.0

            # 4. Струмовий баланс фільтра шини DC:
            # I_C = I_supply + I_regen - I_brake - I_quiescent
            i_cap = i_supply + i_regen - i_brake - self.i_quiescent

            # 5. Інтегрування рівняння dV_bus/dt = I_C / C_bus
            v_bus += (i_cap / self.c_bus) * dt

            # Фіксація піків напруги та перевірка меж безпеки
            if v_bus > v_max:
                v_max = v_bus
            if v_bus < v_min:
                v_min = v_bus
            if v_bus >= self.v_max_safe:
                overvoltage_fault = True

            # Інтегрування енергії
            e_regen_accum += p_regen * dt
            e_brake_accum += (i_brake ** 2) * self.r_brake * dt

            # Запис точок для візуалізації
            if step % record_decimation == 0:
                time_series.append(round(t, 6))
                v_bus_series.append(round(v_bus, 3))
                i_regen_series.append(round(i_regen, 3))
                i_brake_series.append(round(i_brake, 3))
                chopper_state_series.append(chopper_active)

        duty_cycle = (chopper_on_time / t_decel * 100.0) if t_decel > 0 else 0.0

        return SimulationResult(
            duration=t_total,
            v_max=v_max,
            v_min=v_min,
            v_final=v_bus,
            e_regen_total=e_regen_accum,
            e_brake_dissipated=e_brake_accum,
            chopper_active_time=chopper_on_time,
            chopper_duty_cycle=duty_cycle,
            switch_count=self.comparator.switch_count,
            overvoltage_fault=overvoltage_fault,
            time_series=time_series,
            v_bus_series=v_bus_series,
            i_regen_series=i_regen_series,
            i_brake_series=i_brake_series,
            chopper_state_series=chopper_state_series,
        )
