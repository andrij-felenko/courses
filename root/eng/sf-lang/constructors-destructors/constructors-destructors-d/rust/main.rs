struct DeviceHandle {
    fd: i32,
}

impl Drop for DeviceHandle {
    fn drop(&mut self) {
        // Викликається компілятором автоматично в точці втрати власності (scope end)
        unsafe { libc::close(self.fd); }
    }
}
