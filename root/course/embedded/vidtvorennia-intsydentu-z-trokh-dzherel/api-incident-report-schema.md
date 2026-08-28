# 📋 Специфікація мультимодального звіту реконструкції інциденту

Автоматизовані засоби розслідування аварій безпілотних апаратів потребують уніфікованого машиночитаного формату для обміну даними між декодерами логів, інструментами візуалізації траєкторій (PlotJuggler, QGroundControl Replay) та експертними системами класифікації відмов. Без строгої схеми результати злиття трьох асинхронних джерел — бортового бінарного журналу, телеметрії станції керування та відеопотоку — залишаються розрізненими текстовими нотатками або неструктурованими таблицями.

Цей довідник визначає схему даних `incident_report_v1.json`, контракти представлення часових перетворень, структуру маркерів опорних подій, вектор інновацій розбіжності фільтра Калмана та категоризовані діагностичні висновки мультимодального розбору.

## 1. Загальна структура схеми звіту

Кореневий об'єкт звіту містить шість обов'язкових секцій, кожна з яких описує окремий аспект мультимодального розслідування:
1. `metadata` — паспорт інциденту (ідентифікатор борту, серійні номери апаратних модулів, версія польотного стека, конфігурація рами, тривалість запису).
2. `sources` — специфікація та криптографічні хеш-суми SHA-256 усіх вхідних файлів (.bin/.ulg, .tlog, .mp4), що гарантує незмінність доказової бази під час аудиту.
3. `time_sync` — параметри моделі вирівнювання часових шкал (коефіцієнти лінійної регресії, опорні маркери, оцінка залишкової середньоквадратичної похибки).
4. `timeline` — хронологічна послідовність синхронізованих дискретних подій з усіх джерел, приведена до єдиної наносекундної сітки.
5. `anomalies` — виявлені математичні аномалії (стрибки інновацій EKF, вібраційний кліпінг, провали напруги, розсинхрон дій пілота та реакції автопілота).
6. `diagnosis` — фінальний діагностичний висновок розслідування з локалізацією першопричини, коефіцієнтом достовірності та матрицею розподілу відповідальності.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MultimodalIncidentReport",
  "type": "object",
  "required": [
    "metadata",
    "sources",
    "time_sync",
    "timeline",
    "anomalies",
    "diagnosis"
  ],
  "properties": {
    "metadata": { "$ref": "#/$defs/Metadata" },
    "sources": { "$ref": "#/$defs/Sources" },
    "time_sync": { "$ref": "#/$defs/TimeSync" },
    "timeline": {
      "type": "array",
      "items": { "$ref": "#/$defs/TimelineEvent" }
    },
    "anomalies": {
      "type": "array",
      "items": { "$ref": "#/$defs/AnomalyRecord" }
    },
    "diagnosis": { "$ref": "#/$defs/Diagnosis" }
  }
}
```

## 2. Детальна специфікація полів та правил валідації

### 2.1. Секція `sources` (Вхідні модальності даних)

Кожен вхідний потік верифікується за контрольним хешем SHA-256 для виключення можливості випадкової підміни логів або обробки файлів від різних польотів:

- `flight_log`: описує бінарний лог високої частоти.
  - `path` (`string`): відносний або абсолютний шлях до файлу.
  - `sha256` (`string`): 64-символьний шістнадцятковий хеш вмісту.
  - `format` (`enum`): допустимі значення `"ULOG"`, `"DATAFLASH_BIN"`, `"BLACKBOX"`.
  - `sample_rate_hz` (`number`): середня частота опитування інерціального контуру (зазвичай 50–400 Гц).
  - `records_count` (`integer`): загальна кількість розпарсених структур повідомлень.
  - `is_truncated` (`boolean`): прапорець раптового обриву запису (відсутність коректного маркеру кінця файлу EOF).

- `gcs_log`: описує журнал телеметрії наземної станції.
  - `path` (`string`): шлях до файлу `.tlog`.
  - `sha256` (`string`): криптографічний хеш файлу.
  - `format` (`enum`): `"TLOG_MAVLINK1"` або `"TLOG_MAVLINK2"`.
  - `packet_count` (`integer`): кількість прийнятих і відправлених пакетів MAVLink.
  - `packet_loss_pct` (`number`): відсоток втрачених пакетів за лічильником послідовності `seq`.

- `video_stream`: описує відеозапис камери спостереження або FPV-каналу.
  - `path` (`string`): шлях до контейнера MP4 або MKV.
  - `sha256` (`string`): хеш відеофайлу.
  - `duration_sec` (`number`): точна тривалість відеопотоку в секундах.
  - `fps` (`number`): кадрова частота (наприклад, 29.97, 59.94, 60.0).
  - `resolution` (`string`): просторова роздільна здатність матриці (наприклад, `"3840x2160"`).
  - `has_audio_track` (`boolean`): наявність аудіотракту для акустичного вилучення обертів двигунів.
  - `has_osd_telemetry` (`boolean`): наявність графічного накладання параметрів поверх відеоряду.

### 2.2. Секція `time_sync` (Параметри математичної моделі вирівнювання)

Секція фіксує результати розрахунку лінійної моделі прив'язки монотонного бортового часу `t_boot_us` до шкали UTC станції керування:

`t_utc_epoch_ms = (alpha_drift_scale · (t_boot_us / 1000.0)) + beta_offset_ms`

- `alignment_method` (`string`): метод розрахунку (`"ANCHOR_REGRESSION_CROSS_CORRELATION"` або `"MANUAL_OVERRIDE"`).
- `alpha_drift_scale` (`number`): коефіцієнт масштабування часу `α`. Значення `1.0000185` вказує на те, що бортовий кварц випереджає еталонний час на 18.5 мільйонних часток (18.5 ppm).
- `beta_offset_ms` (`number`): початковий зсув епохи `β` у мілісекундах відносно півночі 1 січня 1970 року (Unix Epoch).
- `video_pts_offset_ms` (`number`): абсолютний зсув нульового кадру відеофайлу відносно нульової відмітки `t_boot` мікроконтролера.
- `residual_rms_ms` (`number`): середньоквадратична нев'язка регресії за всіма опорними точками. Для достовірного аналізу значення не повинно перевищувати 5.0 мс.
- `anchor_points` (`array`): перелік верифікованих спільних подій (`name`, `t_boot_ms`, `t_gcs_epoch_ms`, `video_pts_ms`), за якими будувалася лінія регресії.

### 2.3. Секція `timeline` (Синхронізована хронологічна стрічка подій)

Масив об'єктів подій, відсортованих за зростанням уніфікованого часу. Кожен елемент містить три узгоджені часові мітки:

- `event_id` (`integer`): унікальний порядковий номер події в конвеєрі.
- `t_boot_ms` (`number`): час у монотонній системі координат мікроконтролера.
- `t_utc_iso` (`string`): часовий штамп у форматі ISO 8601 UTC (наприклад, `"2026-08-27T10:14:35.230Z"`).
- `video_frame_idx` (`integer`): точний номер відповідного кадру відеозапису.
- `source` (`enum`): первинне джерело події (`"FLIGHT_LOG"`, `"GCS_LOG"`, `"VIDEO_STREAM"`).
- `category` (`enum`): тип події (`"STATE_CHANGE"`, `"COMMAND"`, `"SENSOR_FAILURE"`, `"FAILSAFE"`, `"CRASH_EVENT"`).
- `severity` (`enum`): критичність (`"INFO"`, `"WARNING"`, `"CRITICAL"`, `"EMERGENCY"`).
- `message` (`string`): текстовий опис події.
- `data_payload` (`object`): структурований словник параметрів (наприклад, значення струму, індекс режиму, координати GPS).

### 2.4. Секція `anomalies` (Автоматично класифіковані сигнатури несправностей)

Містить записи про виявлені математичні аномалії, які передували аварії або супроводжували її розвиток:

- `POWER_RAIL_BROWNOUT`: падіння напруги силової шини `V_bat` нижче мінімальної робочої напруги стабілізатора (Brownout Reset) за час < 5 мс без попереднього зниження ємності акумулятора.
- `EKF_INNOVATION_BLOWUP`: зростання нормалізованого інноваційного тесту розширеного фільтра Калмана (`SM_Ratio` або `SV_Ratio`) понад критичний поріг `1.0`, що свідчить про геометричний конфлікт між компасом та супутником GPS.
- `VIBRATION_CLIPPING`: апаратне зашкалювання вихідного каскаду акселерометра (показник `ClipCount > 0`), що викликає втрату справжнього вектора гравітації та уявне зміщення горизонту.
- `MOTOR_SATURATION_LOSS`: досягнення 100% шпаруватості ШІМ або цифрового коду DShot на одному з моторів за відсутності фізичного прискорення рами (сигнатура зриву комутації ESC або відриву лопаті гвинта).
- `COMMAND_TRAJECTORY_DIVERGENCE`: розбіжність між вектором бажання пілота за радіоканалом та реальним кутовим рухом рами.

### 2.5. Секція `diagnosis` (Остаточний експертний висновок)

Підсумок автоматизованого аналізу причинно-наслідкового ланцюга:

- `root_cause_code` (`string`): стандартизований ідентифікатор першопричини за таксономією відмов (наприклад, `"HARDWARE_POWER_LOSS"`, `"SENSOR_MAGNETIC_ANOMALY"`, `"PILOT_CFIT_COLLISION"`, `"ACTUATOR_DESYNC_FAILURE"`).
- `confidence_score` (`number`): числова оцінка достовірності версії від `0.00` до `1.00`, розрахована на основі кількості підтверджених свідчень із різних модальностей.
- `evidence_sources` (`array`): масив ідентифікаторів фактів, що підтвердили діагноз (наприклад, `["FLIGHT_LOG_INSTANT_VOLTAGE_DROP", "GCS_SUDDEN_HEARTBEAT_SILENCE", "VIDEO_AUDIO_INSTANT_MOTOR_SHUTDOWN"]`).
- `summary_uk` (`string`): повний інженерний висновок українською мовою з хронологічним описом розвитку аварійної ситуації.

## 3. Зразок повністю валідного звіту інциденту

Нижче наведено приклад згенерованого звіту реального польотного інциденту, де відбулося раптове розімкнення силового роз'єму батареї під час екстремального гальмування апарата:

```json
{
  "metadata": {
    "report_version": "1.0.0",
    "vehicle_id": "UAV-HEXA-042",
    "flight_datetime": "2026-08-27T10:12:00Z",
    "firmware_type": "ArduPilot Copter",
    "firmware_version": "4.5.1-stable"
  },
  "sources": {
    "flight_log": {
      "path": "logs/00000142.BIN",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "format": "DATAFLASH_BIN",
      "sample_rate_hz": 200,
      "records_count": 84520,
      "is_truncated": true
    },
    "gcs_log": {
      "path": "telemetry/2026-08-27_10-11-58.tlog",
      "sha256": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
      "format": "TLOG_MAVLINK2",
      "packet_count": 4210,
      "packet_loss_pct": 1.4
    },
    "video_stream": {
      "path": "video/FPV_CAM_0142.MP4",
      "sha256": "879fb04212563f4122dca598a39a23dc4da786eff8147c4e72b9807785af1234",
      "duration_sec": 422.5,
      "fps": 60.0,
      "resolution": "3840x2160",
      "has_audio_track": true,
      "has_osd_telemetry": true
    }
  },
  "time_sync": {
    "alignment_method": "ANCHOR_REGRESSION_CROSS_CORRELATION",
    "alpha_drift_scale": 1.0000182,
    "beta_offset_ms": 1724753520114.0,
    "video_pts_offset_ms": -3420.5,
    "residual_rms_ms": 1.15,
    "anchor_points": [
      {
        "name": "ARMING_EVENT",
        "t_boot_ms": 12450.0,
        "t_gcs_epoch_ms": 1724753532564.0,
        "video_pts_ms": 15870.5
      },
      {
        "name": "TAKEOFF_THRUST_SPOOL",
        "t_boot_ms": 18200.0,
        "t_gcs_epoch_ms": 1724753538314.0,
        "video_pts_ms": 21620.5
      },
      {
        "name": "MODE_AUTO_ENTER",
        "t_boot_ms": 65120.0,
        "t_gcs_epoch_ms": 1724753585235.0,
        "video_pts_ms": 68540.5
      },
      {
        "name": "CRASH_IMPACT_SPIKE",
        "t_boot_ms": 422450.0,
        "t_gcs_epoch_ms": 1724753942571.0,
        "video_pts_ms": 425870.5
      }
    ]
  },
  "timeline": [
    {
      "event_id": 1,
      "t_boot_ms": 12450.0,
      "t_utc_iso": "2026-08-27T10:12:12.564Z",
      "video_frame_idx": 952,
      "source": "FLIGHT_LOG",
      "category": "STATE_CHANGE",
      "severity": "INFO",
      "message": "Motors armed: safety switch engaged, pre-arm checks passed",
      "data_payload": { "arm_mode": "ARMED_STICK" }
    },
    {
      "event_id": 48,
      "t_boot_ms": 421800.0,
      "t_utc_iso": "2026-08-27T10:19:01.918Z",
      "video_frame_idx": 25552,
      "source": "FLIGHT_LOG",
      "category": "SENSOR_FAILURE",
      "severity": "WARNING",
      "message": "EKF lane 0 innovation warning: compass variance exceeded threshold (SM=1.34)",
      "data_payload": { "sm_ratio": 1.34, "sv_ratio": 0.22 }
    },
    {
      "event_id": 49,
      "t_boot_ms": 422450.0,
      "t_utc_iso": "2026-08-27T10:19:02.568Z",
      "video_frame_idx": 25591,
      "source": "FLIGHT_LOG",
      "category": "CRASH_EVENT",
      "severity": "EMERGENCY",
      "message": "Primary power rail collapse (V_bat dropped from 22.4V to 0.0V in 0.5ms), log unclosed",
      "data_payload": { "accel_peak_g": 18.4, "last_valid_sector": 4120 }
    }
  ],
  "anomalies": [
    {
      "type": "POWER_RAIL_BROWNOUT",
      "t_start_boot_ms": 422449.5,
      "duration_ms": 0.5,
      "severity_score": 1.0,
      "description": "Раптове розімкнення головного силового роз'єму XT90 під час гальмування"
    }
  ],
  "diagnosis": {
    "root_cause_code": "HARDWARE_POWER_LOSS",
    "confidence_score": 0.98,
    "evidence_sources": [
      "FLIGHT_LOG_INSTANT_VOLTAGE_DROP",
      "GCS_SUDDEN_HEARTBEAT_SILENCE",
      "VIDEO_AUDIO_INSTANT_MOTOR_SHUTDOWN"
    ],
    "summary_uk": "Аварія сталася внаслідок механічного роз'єднання силового кола акумулятора через вібраційне послаблення контакту XT90. Польотний контролер миттєво знеструмився без збереження фінального буфера. Відеозапис підтверджує падіння апарата з нерухомими гвинтами без попередніх команд пілота на вимкнення."
  }
}
```
