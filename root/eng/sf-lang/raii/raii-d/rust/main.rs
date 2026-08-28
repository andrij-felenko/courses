use std::fs::File;
use std::io::{self, Read};

fn read_credentials() -> io::Result<String> {
    // 1. Захоплення ресурсу: відкриття файлу
    let mut file = File::open("secret.key")?; // '?' — раннє повернення при помилці

    let mut content = String::new();
    file.read_to_string(&mut content)?;

    // 2. Успішне повернення:
    // Змінна 'file' виходить зі scope, компілятор автоматично викликає File::drop(&mut file),
    // дескриптор файлу закривається без жодного рядка ручного коду.
    Ok(content)
}
