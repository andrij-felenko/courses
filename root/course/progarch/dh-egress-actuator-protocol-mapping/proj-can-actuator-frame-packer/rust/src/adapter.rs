//! Вихідний адаптер сервоприводу заслінки: трансляція доменних команд у кадри шини CAN DBC.
//!
//! Реалізує шаблон «порти й адаптери» (гексагональну архітектуру):
//! - Квантує неперервну фізичну величину `DamperAngle` у цілочисельний сигнал DBC.
//! - Детерміновано упаковує бітові поля у буфер `[u8; 8]` із врахуванням порядку байтів Little-Endian та Big-Endian.
//! - Веде 4-бітний циклічний лічильник rolling counter (0..15).
//! - Обчислює контрольну суму CRC-8 для захисту цілісності кадру.
//! - Транслює низькорівневі збої шини CAN у типізований результат `Result<OutputReport, ActuatorError>`.

use crate::can::{calculate_crc8_sae_j1850, CanBusError, CanFrame, CanTransceiver, CAN_PAYLOAD_SIZE};
use crate::domain::{
    ActuatorError, DamperActuatorPort, DamperAngle, DamperCommand, OutputReport,
};

/// Ідентифікатор кадру CAN для керування актуатором заслінки згідно зі специфікацією DBC.
pub const DAMPER_CONTROL_FRAME_ID: u32 = 0x120;

/// Масштаб квантування сигналу кута заслінки: 0.1° на дискрет (LSB).
pub const ANGLE_SCALE_DEGREES: f64 = 0.1;

/// Номінальне обмеження кутової швидкості: 45.0°/с (масштаб 0.1°/с -> raw 450).
pub const DEFAULT_SPEED_LIMIT_RAW: u16 = 450;

/// Бітова маска прапорця режиму калібрування (Байт 2, Біт 0).
pub const FLAG_CALIBRATION_MASK: u8 = 0x01;

/// Бітова маска прапорця готовності/активації приводу (Байт 2, Біт 1).
pub const FLAG_ACTUATOR_ENABLE_MASK: u8 = 0x02;

/// Маска 4-бітного лічильника rolling counter (діапазон 0..15).
pub const ROLLING_COUNTER_MASK: u8 = 0x0F;

/// Вихідний адаптер актуатора заслінки.
///
/// Реалізує трейт вихідного порту `DamperActuatorPort`, зв'язуючи чисту бізнес-логіку
/// з фізичним чи тестовим трансивером шини CAN.
pub struct CanDamperActuatorAdapter<T: CanTransceiver> {
    transceiver: T,
    rolling_counter: u8,
}

impl<T: CanTransceiver> CanDamperActuatorAdapter<T> {
    /// Створює новий вихідний адаптер з інжектованим трансивером шини CAN.
    pub fn new(transceiver: T) -> Self {
        Self {
            transceiver,
            rolling_counter: 0,
        }
    }

    /// Повертає незмінне посилання на трансивер шини CAN.
    pub fn transceiver(&self) -> &T {
        &self.transceiver
    }

    /// Повертає змінне посилання на трансивер шини CAN (для тестів та інжекції збоїв).
    pub fn transceiver_mut(&mut self) -> &mut T {
        &mut self.transceiver
    }

    /// Поточне значення циклічного лічильника (0..15).
    pub fn rolling_counter(&self) -> u8 {
        self.rolling_counter
    }

    /// Квантує неперервний фізичний кут `DamperAngle` у цілочисельний сигнал DBC.
    ///
    /// Математична модель: `raw = round((angle_deg - offset) / scale)`.
    /// Для діапазону [0.0°, 90.0°] при кроці 0.1° повертає дискретне значення [0, 900].
    pub fn quantize_angle(angle: DamperAngle) -> u16 {
        let raw = (angle.degrees() / ANGLE_SCALE_DEGREES).round();
        raw.clamp(0.0, 900.0) as u16
    }

    /// Детерміновано упаковує доменну команду у бінарний 8-байтний буфер CAN за специфікацією DBC.
    ///
    /// Розподіл бітових полів у буфері `[u8; 8]`:
    /// - Байт 0..1: Цільовий кут заслінки (16 біт, Little-Endian / Intel).
    /// - Байт 2: Прапорці керування (Біт 0: Калібрування, Біт 1: Активація приводу).
    /// - Байт 3: 4-бітний rolling counter у молодшому ніблі (Bits 0..3).
    /// - Байт 4..5: Обмеження кутової швидкості (16 біт, Big-Endian / Motorola).
    /// - Байт 6: Зарезервований байт пакування (0x00).
    /// - Байт 7: Контрольна сума CRC-8 (SAE J1850) над байтами 0..6.
    pub fn pack_dbc_frame(&self, command: &DamperCommand, sequence: u8) -> CanFrame {
        let mut payload = [0u8; CAN_PAYLOAD_SIZE];

        // 1. Пакування квантованого кута у прямому порядку байтів (Little-Endian / Intel)
        let angle_raw = Self::quantize_angle(command.target_angle());
        payload[0] = (angle_raw & 0xFF) as u8;
        payload[1] = ((angle_raw >> 8) & 0xFF) as u8;

        // 2. Пакування бітових прапорців керування
        let mut control_flags = FLAG_ACTUATOR_ENABLE_MASK;
        if command.is_calibration() {
            control_flags |= FLAG_CALIBRATION_MASK;
        }
        payload[2] = control_flags;

        // 3. Формування 4-бітного лічильника послідовності (rolling counter)
        payload[3] = sequence & ROLLING_COUNTER_MASK;

        // 4. Пакування обмеження швидкості у зворотному порядку байтів (Big-Endian / Motorola)
        let speed_raw = DEFAULT_SPEED_LIMIT_RAW;
        payload[4] = ((speed_raw >> 8) & 0xFF) as u8; // Старший байт (MSB)
        payload[5] = (speed_raw & 0xFF) as u8;        // Молодший байт (LSB)

        // 5. Зарезервований байт вирівнювання структури
        payload[6] = 0x00;

        // 6. Розрахунок контрольної суми CRC-8 над байтами 0..6
        let crc = calculate_crc8_sae_j1850(&payload[0..7]);
        payload[7] = crc;

        CanFrame::new(DAMPER_CONTROL_FRAME_ID, payload)
    }

    /// Транслює низькорівневі помилки шини CAN у доменні коди помилок `ActuatorError`.
    ///
    /// Забезпечує дотримання архітектурної межі: технічні деталі зв'язку не витікають у доменне ядро.
    pub fn map_can_error(error: CanBusError) -> ActuatorError {
        match error {
            CanBusError::Timeout => ActuatorError::BusTimeout,
            CanBusError::BusOff => ActuatorError::HardwareFault(
                "Контролер CAN перейшов в аварійний стан Bus-Off через накопичення помилок передачі".to_string(),
            ),
            CanBusError::TransmitQueueFull => ActuatorError::TransmissionFailed(
                "Буфер черги передачі TX шини CAN переповнений".to_string(),
            ),
            CanBusError::AcknowledgmentLost => ActuatorError::TransmissionFailed(
                "Відсутній апаратний сигнал підтвердження (ACK) від актуатора на шині CAN".to_string(),
            ),
            CanBusError::InvalidDlc(dlc) => {
                ActuatorError::InvalidData(format!("Некоректний DLC кадру шини CAN: {dlc}, очікується 8"))
            }
            CanBusError::DriverError(msg) => {
                ActuatorError::TransmissionFailed(format!("Збій периферійного драйвера шини CAN: {msg}"))
            }
        }
    }
}

impl<T: CanTransceiver> DamperActuatorPort for CanDamperActuatorAdapter<T> {
    fn send_command(&mut self, command: &DamperCommand) -> Result<OutputReport, ActuatorError> {
        let current_sequence = self.rolling_counter;
        let frame = self.pack_dbc_frame(command, current_sequence);

        // Безпечний циклічний інкремент 4-бітного лічильника послідовності (0..15)
        self.rolling_counter = (self.rolling_counter + 1) & ROLLING_COUNTER_MASK;

        // Відправка сформованого кадру CAN у низькорівневий трансивер
        self.transceiver
            .transmit(&frame)
            .map_err(Self::map_can_error)?;

        // Формування чистого доменного звіту про успішну доставку команди в актуатор
        Ok(OutputReport::new(
            command.target_angle(),
            command.target_angle(),
            current_sequence,
            command.is_calibration(),
        ))
    }
}
