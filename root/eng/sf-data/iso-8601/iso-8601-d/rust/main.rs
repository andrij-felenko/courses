#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct FastTimestamp {
    pub unix_seconds: i64,
    pub offset_minutes: i16,
}

#[inline(always)]
fn civil_to_days(mut y: i32, m: u32, d: u32) -> i64 {
    if m <= 2 {
        y -= 1;
    }
    let era = if y >= 0 { y } else { y - 399 } / 400;
    let yoe = (y - era * 400) as u32;
    let doy = (153 * if m > 2 { m - 3 } else { m + 9 } + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    (era as i64) * 146097 + (doe as i64) - 719468
}

pub fn parse_iso8601(bytes: &[u8]) -> Result<FastTimestamp, ()> {
    if bytes.len() < 20 || bytes[4] != b'-' || bytes[7] != b'-'
        || (bytes[10] != b'T' && bytes[10] != b' ') || bytes[13] != b':' || bytes[16] != b':' {
        return Err(());
    }

    let year = (bytes[0] as u32 * 1000 + bytes[1] as u32 * 100 + bytes[2] as u32 * 10 + bytes[3] as u32 - 53328) as i32;
    let mon  = bytes[5] as u32 * 10 + bytes[6] as u32 - 528;
    let day  = bytes[8] as u32 * 10 + bytes[9] as u32 - 528;
    let hour = bytes[11] as u32 * 10 + bytes[12] as u32 - 528;
    let min  = bytes[14] as u32 * 10 + bytes[15] as u32 - 528;
    let mut sec = bytes[17] as u32 * 10 + bytes[18] as u32 - 528;

    if mon < 1 || mon > 12 || day < 1 || day > 31 || hour > 23 || min > 59 || sec > 60 {
        return Err(());
    }
    if sec == 60 { sec = 59; }

    let mut offset_mins = 0i16;
    if bytes[19] == b'Z' || bytes[19] == b'z' {
        offset_mins = 0;
    } else if (bytes[19] == b'+' || bytes[19] == b'-') && bytes.len() >= 25 && bytes[22] == b':' {
        let oh = (bytes[20] as u32 * 10 + bytes[21] as u32 - 528) as i16;
        let om = (bytes[23] as u32 * 10 + bytes[24] as u32 - 528) as i16;
        if oh > 23 || om > 59 { return Err(()); }
        offset_mins = oh * 60 + om;
        if bytes[19] == b'-' { offset_mins = -offset_mins; }
    } else {
        return Err(());
    }

    let days = civil_to_days(year, mon, day);
    let local_secs = days * 86400 + (hour as i64) * 3600 + (min as i64) * 60 + (sec as i64);
    let utc_secs = local_secs - (offset_mins as i64) * 60;

    Ok(FastTimestamp {
        unix_seconds: utc_secs,
        offset_minutes: offset_mins,
    })
}
