#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct IsoDateTime {
    pub unix_seconds: i64,
    pub nanoseconds: u32,
    pub offset_minutes: i16,
    pub leap_second: bool,
}

#[inline(always)]
fn days_from_civil(mut y: i32, m: u32, d: u32) -> i64 {
    if m <= 2 {
        y -= 1;
    }
    let era = if y >= 0 { y } else { y - 399 } / 400;
    let yoe = (y - era * 400) as u32;
    let doy = (153 * if m > 2 { m - 3 } else { m + 9 } + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    (era as i64) * 146097 + (doe as i64) - 719468
}

#[inline(always)]
fn parse2(b: &[u8]) -> u32 {
    (b[0] as u32) * 10 + (b[1] as u32) - 528
}

#[inline(always)]
fn parse4(b: &[u8]) -> u32 {
    (b[0] as u32) * 1000 + (b[1] as u32) * 100 + (b[2] as u32) * 10 + (b[3] as u32) - 53328
}

pub fn parse_iso8601_fast(bytes: &[u8]) -> Result<IsoDateTime, ()> {
    if bytes.len() < 20 {
        return Err(());
    }

    if bytes[4] != b'-' || bytes[7] != b'-' || (bytes[10] != b'T' && bytes[10] != b' ')
        || bytes[13] != b':' || bytes[16] != b':' {
        return Err(());
    }

    let year = parse4(&bytes[0..4]) as i32;
    let month = parse2(&bytes[5..7]);
    let day = parse2(&bytes[8..10]);
    let hour = parse2(&bytes[11..13]);
    let min = parse2(&bytes[14..16]);
    let sec = parse2(&bytes[17..19]);

    if month < 1 || month > 12 || day < 1 || day > 31 || hour > 23 || min > 59 || sec > 60 {
        return Err(());
    }

    let is_leap = sec == 60;
    let eff_sec = if is_leap { 59 } else { sec };

    let mut idx = 19;
    let mut nanos = 0u32;

    if idx < bytes.len() && (bytes[idx] == b'.' || bytes[idx] == b',') {
        idx += 1;
        let mut mult = 100_000_000u32;
        while idx < bytes.len() && bytes[idx] >= b'0' && bytes[idx] <= b'9' {
            if mult > 0 {
                nanos += ((bytes[idx] - b'0') as u32) * mult;
                mult /= 10;
            }
            idx += 1;
        }
    }

    let mut offset_mins = 0i16;
    if idx < bytes.len() {
        if bytes[idx] == b'Z' || bytes[idx] == b'z' {
            offset_mins = 0;
        } else if (bytes[idx] == b'+' || bytes[idx] == b'-') && (bytes.len() - idx >= 6) {
            if bytes[idx + 3] != b':' {
                return Err(());
            }
            let off_h = parse2(&bytes[idx + 1..idx + 3]) as i16;
            let off_m = parse2(&bytes[idx + 4..idx + 6]) as i16;
            if off_h > 23 || off_m > 59 {
                return Err(());
            }
            offset_mins = off_h * 60 + off_m;
            if bytes[idx] == b'-' {
                offset_mins = -offset_mins;
            }
        } else {
            return Err(());
        }
    }

    let days = days_from_civil(year, month, day);
    let local_secs = days * 86400 + (hour as i64) * 3600 + (min as i64) * 60 + (eff_sec as i64);
    let utc_secs = local_secs - (offset_mins as i64) * 60;

    Ok(IsoDateTime {
        unix_seconds: utc_secs,
        nanoseconds: nanos,
        offset_minutes: offset_mins,
        leap_second: is_leap,
    })
}
