use hmac::{Hmac, Mac};
use sha2.Sha256;
use subtle::ConstantTimeEq;

type HmacSha256 = Hmac<Sha256>;

fn sign(key: &[u8], data: &[u8]) -> [u8; 32] {
    let mut mac = HmacSha256::new_from_slice(key)
        .expect("HMAC може приймати ключ будь-якої довжини");
    mac.update(data);
    mac.finalize().into_bytes().into()
}

fn verify(key: &[u8], data: &[u8], expected_mac: &[u8]) -> bool {
    let mut mac = HmacSha256::new_from_slice(key)
        .expect("HMAC може приймати ключ будь-якої довжини");
    mac.update(data);
    // Метод verify_slice використовує ConstantTimeEq
    mac.verify_slice(expected_mac).is_ok()
}
