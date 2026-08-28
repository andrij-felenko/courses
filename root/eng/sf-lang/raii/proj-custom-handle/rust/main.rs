use std::os::raw::c_int;

// Власний безпечний дескриптор
pub struct SafeFd {
    fd: c_int,
}

impl SafeFd {
    pub const INVALID: c_int = -1;

    // Створення обгортки з перевіркою валідності
    pub fn new(fd: c_int) -> Option<Self> {
        if fd >= 0 {
            Some(Self { fd })
        } else {
            None
        }
    }

    // Доступ до сирого дескриптора без передачі власності
    pub fn raw(&self) -> c_int {
        self.fd
    }

    // Відчуження дескриптора (передача сирого значення без виклику Drop)
    pub fn into_raw(mut self) -> c_int {
        let fd = self.fd;
        self.fd = Self::INVALID;
        std::mem::forget(self); // скасовує виклик Drop
        fd
    }
}

// Реалізація RAII-очищення через типаж Drop
impl Drop for SafeFd {
    fn drop(&mut self) {
        if self.fd >= 0 {
            unsafe {
                libc::close(self.fd);
            }
        }
    }
}
