//! Двійкові структури кадру шини CAN, апаратні статуси та алгоритм контрольної суми CRC-8.

use std::fmt;

/// Фіксована місткість корисного навантаження стандартного кадру Classical CAN (8 байтів).
pub const CAN_PAYLOAD_SIZE: usize = 8;

/// Структура двійкового кадру шини CAN.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CanFrame {
    id: u32,
    dlc: u8,
    data: [u8; CAN_PAYLOAD_SIZE],
}

impl CanFrame {
    /// Створює новий кадр Classical CAN із фіксованим розміром DLC = 8.
    pub fn new(id: u32, data: [u8; CAN_PAYLOAD_SIZE]) -> Self {
        Self {
            id,
            dlc: CAN_PAYLOAD_SIZE as u8,
            data,
        }
    }

    /// Створює кадр CAN із явно визначеним DLC (0..=8).
    pub fn with_dlc(id: u32, dlc: u8, data: [u8; CAN_PAYLOAD_SIZE]) -> Result<Self, CanBusError> {
        if dlc as usize > CAN_PAYLOAD_SIZE {
            return Err(CanBusError::InvalidDlc(dlc));
        }
        Ok(Self { id, dlc, data })
    }

    /// Ідентифікатор кадру CAN (Standard 11-bit або Extended 29-bit).
    #[inline]
    pub fn id(&self) -> u32 {
        self.id
    }

    /// Код довжини даних (Data Length Code).
    #[inline]
    pub fn dlc(&self) -> u8 {
        self.dlc
    }

    /// Посилання на фіксований 8-байтний буфер корисного навантаження.
    #[inline]
    pub fn data(&self) -> &[u8; CAN_PAYLOAD_SIZE] {
        &self.data
    }

    /// Змінне посилання на буфер корисного навантаження.
    #[inline]
    pub fn data_mut(&mut self) -> &mut [u8; CAN_PAYLOAD_SIZE] {
        &mut self.data
    }

    /// Повертає форматований шістнадцятковий дамп байтів корисного навантаження.
    pub fn hex_dump(&self) -> String {
        self.data
            .iter()
            .take(self.dlc as usize)
            .map(|b| format!("{b:02X}"))
            .collect::<Vec<_>>()
            .join(" ")
    }
}

impl fmt::Display for CanFrame {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "CanFrame(ID: 0x{:03X}, DLC: {}, Payload: [{}])",
            self.id,
            self.dlc,
            self.hex_dump()
        )
    }
}

/// Апаратні та протокольні помилки шини CAN.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CanBusError {
    /// Таймаут передачі кадру в фізичний канал.
    Timeout,
    /// Контролер CAN перейшов в аварійний стан Bus-Off через критичний рівень помилок TEC.
    BusOff,
    /// Черга передачі кадру (TX Mailbox) заповнена.
    TransmitQueueFull,
    /// Втрачено сигнал апаратного підтвердження (ACK) від актуатора.
    AcknowledgmentLost,
    /// Передано некоректну довжину DLC (> 8 для Classical CAN).
    InvalidDlc(u8),
    /// Інша апаратна помилка периферійного драйвера CAN.
    DriverError(String),
}

impl fmt::Display for CanBusError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Timeout => write!(f, "Таймаут шини CAN"),
            Self::BusOff => write!(f, "Контролер CAN у стані Bus-Off"),
            Self::TransmitQueueFull => write!(f, "Буфер передачі TX шини CAN переповнено"),
            Self::AcknowledgmentLost => write!(f, "Втрачено сигнал підтвердження ACK"),
            Self::InvalidDlc(dlc) => write!(f, "Некоректний DLC кадру CAN: {dlc}"),
            Self::DriverError(msg) => write!(f, "Помилка драйвера CAN: {msg}"),
        }
    }
}

impl std::error::Error for CanBusError {}

/// Трейт низькорівневого каналу зв'язку шини CAN для передачі сформованого кадру `CanFrame`
/// в апаратну периферію або віртуальний канал тестового емулятора.
pub trait CanTransceiver {
    /// Передає двійковий кадр `CanFrame` у шину.
    fn transmit(&mut self, frame: &CanFrame) -> Result<(), CanBusError>;
}

/// Обчислює 8-бітну контрольну суму CRC-8 за поліномом SAE J1850 (`x^8 + x^4 + x^3 + x^2 + 1` = 0x1D).
///
/// Параметри протоколу:
/// - Поліном: `0x1D`
/// - Початкове значення: `0xFF`
/// - Фінальна операція XOR: `0xFF`
///
/// Використовується в автомобільних специфікаціях DBC для верифікації цілісності даних
/// актуаторів у критичних вузлах керування.
pub fn calculate_crc8_sae_j1850(data: &[u8]) -> u8 {
    let mut crc: u8 = 0xFF;
    for &byte in data {
        crc ^= byte;
        for _ in 0..8 {
            if (crc & 0x80) != 0 {
                crc = (crc << 1) ^ 0x1D;
            } else {
                crc <<= 1;
            }
        }
    }
    crc ^ 0xFF
}
