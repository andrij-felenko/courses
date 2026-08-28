// Cargo.toml: serialport = "4"
use std::io::{BufRead, BufReader, Write};
use std::time::Duration;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = "COM7"; // Linux: "/dev/ttyUSB0", macOS: "/dev/cu.SLAB_USBtoUART"
    let baud = 115_200;

    let mut port = serialport::new(path, baud)
        .data_bits(serialport::DataBits::Eight)
        .parity(serialport::Parity::None)
        .stop_bits(serialport::StopBits::One)
        .timeout(Duration::from_millis(1000))
        .open()?;

    println!("Відкрито {path} на {baud} бод.");
    port.write_all(b"status\n")?;          // надіслати команду

    // окремий читач для рядкового буферування; клон даскриптора порту
    let reader = port.try_clone()?;
    let mut buf = BufReader::new(reader);
    let mut line = String::new();
    loop {
        line.clear();
        match buf.read_line(&mut line) {
            Ok(0) => break,                       // порт закрито
            Ok(_) => print!("{line}"),
            Err(ref e) if e.kind() == std::io::ErrorKind::TimedOut => continue,
            Err(e) => return Err(e.into()),
        }
    }
    Ok(())
}
