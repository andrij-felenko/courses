//! Доменний шар керування сервоприводом повітряної заслінки.
//!
//! Цей модуль містить чисту бізнес-логіку:
//! - Тип-значення `DamperAngle` (Newtype) із гарантією збереження фізичного інваріанта [0.0°, 90.0°].
//! - Доменну команду `DamperCommand`.
//! - Трейт вихідного порту `DamperActuatorPort` (шаблон «порти й адаптери»).
//! - Доменний звіт про виконання команди `OutputReport`.
//! - Типізоване перерахування доменних помилок `ActuatorError`.
//!
//! Модуль є суворо ізольованим від апаратних протоколів (CAN, Modbus, SPI тощо).

use std::fmt;

/// Помилка валідації кута повороту заслінки при конструюванні `DamperAngle`.
#[derive(Debug, Clone, PartialEq)]
pub enum DamperAngleError {
    /// Значення виходить за межі фізично допустимого діапазону [0.0°, 90.0°].
    OutOfRange { value: f64, min: f64, max: f64 },
    /// Значення є нечисловим (NaN).
    NotANumber,
}

impl fmt::Display for DamperAngleError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::OutOfRange { value, min, max } => {
                write!(
                    f,
                    "Кут заслінки {:.2}° виходить за допустимий діапазон [{:.1}°, {:.1}°]",
                    value, min, max
                )
            }
            Self::NotANumber => write!(f, "Кут заслінки не може бути нечисловим значенням (NaN)"),
        }
    }
}

impl std::error::Error for DamperAngleError {}

/// Безпечний тип-значення (Newtype), що гарантує валідацію допустимого фізичного діапазону
/// кута заслінки [0.0°, 90.0°] ще на етапі конструювання об'єкта.
///
/// Унеможливлює існування невалідного стану в доменному ядрі програми.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct DamperAngle(f64);

impl DamperAngle {
    /// Мінімальний фізичний кут повороту (заслінка повністю закрита).
    pub const MIN_DEGREES: f64 = 0.0;
    /// Максимальний фізичний кут повороту (заслінка повністю відкрита).
    pub const MAX_DEGREES: f64 = 90.0;

    /// Створює новий екземпляр `DamperAngle`, перевіряючи інваріант діапазону [0.0°, 90.0°].
    pub fn new(degrees: f64) -> Result<Self, DamperAngleError> {
        if degrees.is_nan() {
            return Err(DamperAngleError::NotANumber);
        }
        if !(Self::MIN_DEGREES..=Self::MAX_DEGREES).contains(&degrees) {
            return Err(DamperAngleError::OutOfRange {
                value: degrees,
                min: Self::MIN_DEGREES,
                max: Self::MAX_DEGREES,
            });
        }
        Ok(Self(degrees))
    }

    /// Повертає значення кута в градусах як число з плаваючою крапкою.
    #[inline]
    pub fn degrees(&self) -> f64 {
        self.0
    }
}

impl fmt::Display for DamperAngle {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:.1}°", self.0)
    }
}

/// Доменна команда керування заслінкою.
///
/// Інкапсулює валідований цільовий кут повороту `DamperAngle` та прапорець запуску
/// процедури калібрування нульового положення.
#[derive(Debug, Clone, PartialEq)]
pub struct DamperCommand {
    target_angle: DamperAngle,
    calibrate: bool,
}

impl DamperCommand {
    /// Створює нову доменну команду.
    pub fn new(target_angle: DamperAngle, calibrate: bool) -> Self {
        Self {
            target_angle,
            calibrate,
        }
    }

    /// Цільовий кут заслінки.
    #[inline]
    pub fn target_angle(&self) -> DamperAngle {
        self.target_angle
    }

    /// Чи є команда запитом на калібрування нульової точки актуатора.
    #[inline]
    pub fn is_calibration(&self) -> bool {
        self.calibrate
    }
}

impl fmt::Display for DamperCommand {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "DamperCommand(цільовий кут: {}, калібрування: {})",
            self.target_angle, self.calibrate
        )
    }
}

/// Доменний звіт про успішне виконання команди актуатором із підтвердженим фізичним положенням.
#[derive(Debug, Clone, PartialEq)]
pub struct OutputReport {
    target_angle: DamperAngle,
    confirmed_angle: DamperAngle,
    sequence_number: u8,
    is_calibrated: bool,
}

impl OutputReport {
    /// Створює новий екземпляр звіту.
    pub fn new(
        target_angle: DamperAngle,
        confirmed_angle: DamperAngle,
        sequence_number: u8,
        is_calibrated: bool,
    ) -> Self {
        Self {
            target_angle,
            confirmed_angle,
            sequence_number,
            is_calibrated,
        }
    }

    /// Запитаний доменний цільовий кут.
    #[inline]
    pub fn target_angle(&self) -> DamperAngle {
        self.target_angle
    }

    /// Підтверджений актуатором фізичний кут після прийому команди.
    #[inline]
    pub fn confirmed_angle(&self) -> DamperAngle {
        self.confirmed_angle
    }

    /// Номер послідовності команди (rolling counter), зафіксований протоколом.
    #[inline]
    pub fn sequence_number(&self) -> u8 {
        self.sequence_number
    }

    /// Чи було підтверджено режим калібрування актуатора.
    #[inline]
    pub fn is_calibrated(&self) -> bool {
        self.is_calibrated
    }
}

impl fmt::Display for OutputReport {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "OutputReport(ціль: {}, підтверджено: {}, seq: {}, калібровано: {})",
            self.target_angle, self.confirmed_angle, self.sequence_number, self.is_calibrated
        )
    }
}

/// Типізоване перерахування доменних помилок актуатора.
///
/// Дозволяє прикладному ядру приймати архітектурні рішення при відмовах обладнання
/// без витоку специфіки шини передачі даних у бізнес-логіку.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ActuatorError {
    /// Збій відправки команди в канал зв'язку (наприклад, переповнення черги TX).
    TransmissionFailed(String),
    /// Таймаут очікування звільнення каналу або відповіді від актуатора.
    BusTimeout,
    /// Некоректні параметри або спотворені бінарні дані протоколу.
    InvalidData(String),
    /// Апаратна несправність актуатора або перехід шини в аварійний стан.
    HardwareFault(String),
}

impl fmt::Display for ActuatorError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::TransmissionFailed(msg) => write!(f, "Збій передачі команди актуатору: {msg}"),
            Self::BusTimeout => write!(f, "Таймаут шини зв'язку з актуатором"),
            Self::InvalidData(msg) => write!(f, "Некоректні протокольні дані: {msg}"),
            Self::HardwareFault(msg) => write!(f, "Апаратна аварія актуатора: {msg}"),
        }
    }
}

impl std::error::Error for ActuatorError {}

/// Трейт вихідного порту (Egress Port), що оголошує абстрактний контракт взаємодії бізнес-логіки
/// з актуатором без витоку деталей шини.
///
/// Доменне ядро володіє цим трейтом та викликає його методи для зміни фізичного стану заслінки.
pub trait DamperActuatorPort {
    /// Відправляє команду актуатору та повертає підтверджений звіт або доменну помилку.
    fn send_command(&mut self, command: &DamperCommand) -> Result<OutputReport, ActuatorError>;
}
