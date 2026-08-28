// ── Довірений доменний об'єкт: існує ⟺ всі поля пройшли розбір ──
pub struct Command { pub device_id: DeviceId, pub target: Celsius, pub action: Action }

pub fn parse_command(body: &str) -> Result<Command, Vec<FieldError>> {
    // 1. ФОРМА: чи це взагалі JSON-об'єкт?
    let root: Value = serde_json::from_str(body)
        .map_err(|_| vec![FieldError { field: "(корінь)", message: "не валідний JSON".into() }])?;
    let obj = root.as_object()
        .ok_or_else(|| vec![FieldError { field: "(корінь)", message: "очікувано об'єкт".into() }])?;

    // 2. ПОЛЯ: кожне — незалежно, у свій Result
    let id     = DeviceId::parse(obj.get("deviceId"));
    let target = Celsius::parse(obj.get("targetTemp"));
    let action = Action::parse(obj.get("action"));

    // 3. РОЗВИЛКА: усі Ok — складаємо; інакше — збираємо ВЕСЬ список
    match (id, target, action) {
        (Ok(device_id), Ok(target), Ok(action)) =>
            Ok(Command { device_id, target, action }),
        (id, target, action) => {
            let mut errors = Vec::new();
            if let Err(m) = id     { errors.push(FieldError { field: "deviceId",   message: m }); }
            if let Err(m) = target { errors.push(FieldError { field: "targetTemp", message: m }); }
            if let Err(m) = action { errors.push(FieldError { field: "action",     message: m }); }
            Err(errors)
        }
    }
}
