//! Точка входу та тестовий стенд: верифікація вихідного порту й адаптера CAN DBC.
//!
//! Модуль демонструє:
//! - Ініціалізацію доменного ядра та відправку команд через абстрактний порт `DamperActuatorPort`.
//! - Роботу тестового емулятора `FakeCanTransceiver`.
//! - Інспекцію двійкових полів кадру CAN (маски, Little-Endian, Big-Endian, CRC-8).
//! - Циклічний інкремент 4-бітного лічильника rolling counter.
//! - Захист архітектурної межі: ізоляцію ядра від апаратних помилок шини.

mod adapter;
mod can;
mod domain;

use adapter::CanDamperActuatorAdapter;
use can::{CanBusError, CanFrame, CanTransceiver};
use domain::{ActuatorError, DamperActuatorPort, DamperAngle, DamperCommand, OutputReport};

/// Тестовий емулятор трансивера шини CAN.
///
/// Перехоплює відправлені кадри `CanFrame` в оперативній пам'яті для верифікації
/// сформованих бінарних масок у тестах без фізичного підключення до шини або мікроконтролера.
#[derive(Debug, Default, Clone)]
pub struct FakeCanTransceiver {
    sent_frames: Vec<CanFrame>,
    injected_error: Option<CanBusError>,
}

impl FakeCanTransceiver {
    /// Створює новий тестовий емулятор із порожнім буфером кадрів.
    pub fn new() -> Self {
        Self::default()
    }

    /// Створює емулятор, налаштований на миттєве повернення помилки шини.
    pub fn with_error(error: CanBusError) -> Self {
        Self {
            sent_frames: Vec::new(),
            injected_error: Some(error),
        }
    }

    /// Повертає список усіх перехоплених кадрів CAN.
    pub fn sent_frames(&self) -> &[CanFrame] {
        &self.sent_frames
    }

    /// Повертає останній переданий кадр CAN.
    pub fn last_frame(&self) -> Option<&CanFrame> {
        self.sent_frames.last()
    }

    /// Очищає буфер захоплених кадрів.
    pub fn clear(&mut self) {
        self.sent_frames.clear();
    }

    /// Впроваджує штучний збій каналу зв'язку для верифікації обробки помилок.
    pub fn inject_error(&mut self, error: CanBusError) {
        self.injected_error = Some(error);
    }

    /// Скидає впроваджену помилку для відновлення нормальної роботи шини.
    pub fn clear_error(&mut self) {
        self.injected_error = None;
    }
}

impl CanTransceiver for FakeCanTransceiver {
    fn transmit(&mut self, frame: &CanFrame) -> Result<(), CanBusError> {
        if let Some(ref err) = self.injected_error {
            return Err(err.clone());
        }
        self.sent_frames.push(frame.clone());
        Ok(())
    }
}

/// Прикладна доменна служба керування кліматом.
///
/// Залежить виключно від абстрактного вихідного порту `DamperActuatorPort`
/// і не має жодного знання про шину CAN, байти чи контрольні суми.
pub struct ClimateControlService<'a> {
    actuator_port: &'a mut dyn DamperActuatorPort,
}

impl<'a> ClimateControlService<'a> {
    /// Створює службу клімат-контролю з інжектованим вихідним портом.
    pub fn new(actuator_port: &'a mut dyn DamperActuatorPort) -> Self {
        Self { actuator_port }
    }

    /// Регулює кут відкриття заслінки у межах фізичного діапазону.
    pub fn adjust_damper(&mut self, degrees: f64) -> Result<OutputReport, ActuatorError> {
        let angle = DamperAngle::new(degrees).map_err(|err| {
            ActuatorError::InvalidData(format!("Помилка валідації доменного кута: {err}"))
        })?;
        let command = DamperCommand::new(angle, false);
        self.actuator_port.send_command(&command)
    }

    /// Виконує калібрування нульового положення заслінки.
    pub fn calibrate_damper(&mut self) -> Result<OutputReport, ActuatorError> {
        let zero_angle = DamperAngle::new(0.0).map_err(|err| {
            ActuatorError::InvalidData(format!("Помилка валідації доменного кута: {err}"))
        })?;
        let command = DamperCommand::new(zero_angle, true);
        self.actuator_port.send_command(&command)
    }
}

fn main() {
    println!("=== Архітектура програмних систем: Порти й адаптери (Трансляція в CAN DBC) ===");

    // 1. Створення тестового трансивера та вихідного адаптера
    let transceiver = FakeCanTransceiver::new();
    let mut adapter = CanDamperActuatorAdapter::new(transceiver);

    // 2. Демонстрація виконання доменної команди позиціонування на 45.0°
    println!("\n[1] Відправка нормальної команди позиціонування на 45.0° через доменний сервіс...");
    {
        let mut service = ClimateControlService::new(&mut adapter);
        match service.adjust_damper(45.0) {
            Ok(report) => {
                println!("  -> Доменний звіт успіху: {report}");
            }
            Err(e) => eprintln!("  -> Доменна помилка: {e}"),
        }
    }

    // 3. Інспекція структури сформованого бінарного кадру CAN у тестовому шпигуні
    if let Some(frame) = adapter.transceiver().last_frame() {
        println!("  -> Перехоплений двійковий кадр шини CAN: {frame}");
        println!("  -> Hex-дамп корисного навантаження:      {}", frame.hex_dump());
        let raw_angle = u16::from_le_bytes([frame.data()[0], frame.data()[1]]);
        println!(
            "     * Байти 0..1 (Кут Little-Endian): 0x{:02X} 0x{:02X} -> raw: {} (фізично {:.1}°)",
            frame.data()[0], frame.data()[1], raw_angle, (raw_angle as f64) * 0.1
        );
        println!(
            "     * Байт 2 (Прапорці):              0x{:02X} (Enable={}, Calibrate={})",
            frame.data()[2],
            (frame.data()[2] & 0x02) != 0,
            (frame.data()[2] & 0x01) != 0
        );
        println!(
            "     * Байт 3 (Rolling Counter):       {}",
            frame.data()[3] & 0x0F
        );
        let raw_speed = u16::from_be_bytes([frame.data()[4], frame.data()[5]]);
        println!(
            "     * Байти 4..5 (Швидкість Big-Endian): 0x{:02X} 0x{:02X} -> raw: {} (фізично {:.1}°/с)",
            frame.data()[4], frame.data()[5], raw_speed, (raw_speed as f64) * 0.1
        );
        println!("     * Байт 7 (CRC-8 SAE J1850):       0x{:02X}", frame.data()[7]);
    }

    // 4. Демонстрація виконання команди калібрування на 0.0°
    println!("\n[2] Відправка команди калібрування актуатора на 0.0°...");
    {
        let mut service = ClimateControlService::new(&mut adapter);
        match service.calibrate_damper() {
            Ok(report) => {
                println!("  -> Доменний звіт калібрування: {report}");
            }
            Err(e) => eprintln!("  -> Помилка: {e}"),
        }
    }

    if let Some(frame) = adapter.transceiver().last_frame() {
        println!("  -> Перехоплений кадр калібрування: {frame}");
        println!(
            "     * Байт 2: 0x{:02X} (Біт 0 = 1: режим калібрування активовано)",
            frame.data()[2]
        );
        println!("     * Байт 3: {} (rolling counter інкрементовано)", frame.data()[3]);
    }

    // 5. Демонстрація циклічного інкременту лічильника послідовності (0..15)
    println!("\n[3] Демонстрація циклічного інкременту лічильника послідовності (0..15)...");
    for i in 2..=16 {
        let angle = DamperAngle::new((i as f64) * 2.0).unwrap();
        let cmd = DamperCommand::new(angle, false);
        let report = adapter.send_command(&cmd).unwrap();
        let frame = adapter.transceiver().last_frame().unwrap();
        println!(
            "  -> Ітерація {:2} | Доменний Seq: {:2} | Байт 3 кадру: {:2} | CRC-8: 0x{:02X}",
            i,
            report.sequence_number(),
            frame.data()[3] & 0x0F,
            frame.data()[7]
        );
    }

    // 6. Демонстрація ізоляції домену при збої шини CAN
    println!("\n[4] Демонстрація стійкості архітектурної межі: симуляція збою шини CAN (Timeout)...");
    adapter.transceiver_mut().inject_error(CanBusError::Timeout);
    {
        let mut service = ClimateControlService::new(&mut adapter);
        match service.adjust_damper(30.0) {
            Ok(_) => println!("  -> Неочікуване виконання команди"),
            Err(e) => {
                println!("  -> Отримано чисту типізовану доменну помилку: {e}");
                println!("  -> Жодна внутрішня деталь шини CAN не просочилася в доменне ядро!");
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::can::{calculate_crc8_sae_j1850, CanBusError};
    use crate::domain::{DamperAngle, DamperAngleError};

    #[test]
    fn test_damper_angle_valid_bounds() {
        assert!(DamperAngle::new(0.0).is_ok());
        assert!(DamperAngle::new(45.0).is_ok());
        assert!(DamperAngle::new(90.0).is_ok());
    }

    #[test]
    fn test_damper_angle_out_of_range_rejected() {
        match DamperAngle::new(-0.1) {
            Err(DamperAngleError::OutOfRange { value, min, max }) => {
                assert!((value - (-0.1)).abs() < 1e-6);
                assert_eq!(min, 0.0);
                assert_eq!(max, 90.0);
            }
            _ => panic!("Очікувалась помилка OutOfRange для від'ємного кута"),
        }

        match DamperAngle::new(90.01) {
            Err(DamperAngleError::OutOfRange { value, min, max }) => {
                assert!((value - 90.01).abs() < 1e-6);
                assert_eq!(min, 0.0);
                assert_eq!(max, 90.0);
            }
            _ => panic!("Очікувалась помилка OutOfRange для кута > 90.0°"),
        }

        match DamperAngle::new(f64::NAN) {
            Err(DamperAngleError::NotANumber) => {}
            _ => panic!("Очікувалась помилка NotANumber для NaN"),
        }
    }

    #[test]
    fn test_dbc_angle_quantization_and_little_endian() {
        let transceiver = FakeCanTransceiver::new();
        let mut adapter = CanDamperActuatorAdapter::new(transceiver);

        // 0.0° -> raw = 0 (0x0000)
        let angle_0 = DamperAngle::new(0.0).unwrap();
        let cmd_0 = DamperCommand::new(angle_0, false);
        adapter.send_command(&cmd_0).unwrap();
        let frame_0 = adapter.transceiver().last_frame().unwrap();
        assert_eq!(frame_0.data()[0], 0x00);
        assert_eq!(frame_0.data()[1], 0x00);

        // 45.0° -> raw = 450 (0x01C2) -> Little-Endian: Байт 0 = 0xC2, Байт 1 = 0x01
        let angle_45 = DamperAngle::new(45.0).unwrap();
        let cmd_45 = DamperCommand::new(angle_45, false);
        adapter.send_command(&cmd_45).unwrap();
        let frame_45 = adapter.transceiver().last_frame().unwrap();
        assert_eq!(frame_45.data()[0], 0xC2);
        assert_eq!(frame_45.data()[1], 0x01);

        // 90.0° -> raw = 900 (0x0384) -> Little-Endian: Байт 0 = 0x84, Байт 1 = 0x03
        let angle_90 = DamperAngle::new(90.0).unwrap();
        let cmd_90 = DamperCommand::new(angle_90, false);
        adapter.send_command(&cmd_90).unwrap();
        let frame_90 = adapter.transceiver().last_frame().unwrap();
        assert_eq!(frame_90.data()[0], 0x84);
        assert_eq!(frame_90.data()[1], 0x03);
    }

    #[test]
    fn test_dbc_control_flags_bitmask() {
        let transceiver = FakeCanTransceiver::new();
        let mut adapter = CanDamperActuatorAdapter::new(transceiver);

        // Звичайна команда: Enable = 1 (Біт 1), Calibrate = 0 (Біт 0) => 0x02
        let angle = DamperAngle::new(10.0).unwrap();
        let normal_cmd = DamperCommand::new(angle, false);
        adapter.send_command(&normal_cmd).unwrap();
        let frame_normal = adapter.transceiver().last_frame().unwrap();
        assert_eq!(frame_normal.data()[2], 0x02);

        // Команда калібрування: Enable = 1 (Біт 1), Calibrate = 1 (Біт 0) => 0x03
        let cal_cmd = DamperCommand::new(angle, true);
        adapter.send_command(&cal_cmd).unwrap();
        let frame_cal = adapter.transceiver().last_frame().unwrap();
        assert_eq!(frame_cal.data()[2], 0x03);
    }

    #[test]
    fn test_motorola_big_endian_speed_limit() {
        let transceiver = FakeCanTransceiver::new();
        let mut adapter = CanDamperActuatorAdapter::new(transceiver);

        let angle = DamperAngle::new(20.0).unwrap();
        let cmd = DamperCommand::new(angle, false);
        adapter.send_command(&cmd).unwrap();
        let frame = adapter.transceiver().last_frame().unwrap();

        // Швидкість за замовчуванням: 45.0°/с -> raw 450 (0x01C2)
        // Big-Endian: Байт 4 (MSB) = 0x01, Байт 5 (LSB) = 0xC2
        assert_eq!(frame.data()[4], 0x01);
        assert_eq!(frame.data()[5], 0xC2);
    }

    #[test]
    fn test_rolling_counter_cyclic_rollover() {
        let transceiver = FakeCanTransceiver::new();
        let mut adapter = CanDamperActuatorAdapter::new(transceiver);
        let angle = DamperAngle::new(15.0).unwrap();
        let cmd = DamperCommand::new(angle, false);

        // Відправляємо 16 команд (індекси лічильника 0..=15)
        for expected_seq in 0..=15 {
            let report = adapter.send_command(&cmd).unwrap();
            assert_eq!(report.sequence_number(), expected_seq);
            let frame = adapter.transceiver().last_frame().unwrap();
            assert_eq!(frame.data()[3] & 0x0F, expected_seq);
        }

        // 17-та команда повинна скинути лічильник на 0 (циклічний rollover)
        let report_rollover = adapter.send_command(&cmd).unwrap();
        assert_eq!(report_rollover.sequence_number(), 0);
        let frame_rollover = adapter.transceiver().last_frame().unwrap();
        assert_eq!(frame_rollover.data()[3] & 0x0F, 0);
    }

    #[test]
    fn test_crc8_sae_j1850_integrity() {
        let transceiver = FakeCanTransceiver::new();
        let mut adapter = CanDamperActuatorAdapter::new(transceiver);
        let angle = DamperAngle::new(30.0).unwrap();
        let cmd = DamperCommand::new(angle, false);

        adapter.send_command(&cmd).unwrap();
        let frame = adapter.transceiver().last_frame().unwrap();

        let expected_crc = calculate_crc8_sae_j1850(&frame.data()[0..7]);
        assert_eq!(frame.data()[7], expected_crc);

        // Зміна навіть одного біта в даних змінює CRC-8
        let mut corrupted_payload = *frame.data();
        corrupted_payload[0] ^= 0x01;
        let corrupted_crc = calculate_crc8_sae_j1850(&corrupted_payload[0..7]);
        assert_ne!(frame.data()[7], corrupted_crc);
    }

    #[test]
    fn test_error_translation_without_bus_leak() {
        let mut transceiver = FakeCanTransceiver::new();
        transceiver.inject_error(CanBusError::Timeout);
        let mut adapter = CanDamperActuatorAdapter::new(transceiver);

        let angle = DamperAngle::new(25.0).unwrap();
        let cmd = DamperCommand::new(angle, false);

        // Перевіряємо трансляцію Timeout
        let result = adapter.send_command(&cmd);
        assert_eq!(result, Err(ActuatorError::BusTimeout));

        // Перевіряємо трансляцію переповнення черги TX
        adapter.transceiver_mut().inject_error(CanBusError::TransmitQueueFull);
        let result_tx = adapter.send_command(&cmd);
        match result_tx {
            Err(ActuatorError::TransmissionFailed(msg)) => {
                assert!(msg.contains("переповнений"));
            }
            _ => panic!("Очікувалась TransmissionFailed"),
        }

        // Перевіряємо трансляцію стану Bus-Off
        adapter.transceiver_mut().inject_error(CanBusError::BusOff);
        let result_busoff = adapter.send_command(&cmd);
        match result_busoff {
            Err(ActuatorError::HardwareFault(msg)) => {
                assert!(msg.contains("Bus-Off"));
            }
            _ => panic!("Очікувалась HardwareFault"),
        }
    }
}
