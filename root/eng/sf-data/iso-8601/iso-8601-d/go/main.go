package iso8601

import (
	"errors"
	"time"
)

var ErrInvalidTimestamp = errors.New("malformed iso8601 timestamp")

func civilToDays(y int, m, d uint) int64 {
	if m <= 2 {
		y--
	}
	era := y / 400
	if y < 0 {
		era = (y - 399) / 400
	}
	yoe := uint(y - era*400)
	var mo uint = m + 9
	if m > 2 {
		mo = m - 3
	}
	doy := (153*mo+2)/5 + d - 1
	doe := yoe*365 + yoe/4 - yoe/100 + doy
	return int64(era)*146097 + int64(doe) - 719468
}

func ParseFastUTC(s string) (time.Time, error) {
	if len(s) < 20 || s[4] != '-' || s[7] != '-' ||
		(s[10] != 'T' && s[10] != ' ') || s[13] != ':' || s[16] != ':' {
		return time.Time{}, ErrInvalidTimestamp
	}

	year := int(uint(s[0])*1000 + uint(s[1])*100 + uint(s[2])*10 + uint(s[3]) - 53328)
	mon := uint(s[5])*10 + uint(s[6]) - 528
	day := uint(s[8])*10 + uint(s[9]) - 528
	hour := uint(s[11])*10 + uint(s[12]) - 528
	min := uint(s[14])*10 + uint(s[15]) - 528
	sec := uint(s[17])*10 + uint(s[18]) - 528

	if mon < 1 || mon > 12 || day < 1 || day > 31 || hour > 23 || min > 59 || sec > 60 {
		return time.Time{}, ErrInvalidTimestamp
	}
	if sec == 60 {
		sec = 59
	}

	var offsetSecs int64
	if s[19] == 'Z' || s[19] == 'z' {
		offsetSecs = 0
	} else if (s[19] == '+' || s[19] == '-') && len(s) >= 25 && s[22] == ':') {
		oh := int64(uint(s[20])*10 + uint(s[21]) - 528)
		om := int64(uint(s[23])*10 + uint(s[24]) - 528)
		if oh > 23 || om > 59 {
			return time.Time{}, ErrInvalidTimestamp
		}
		offsetSecs = oh*3600 + om*60
		if s[19] == '-' {
			offsetSecs = -offsetSecs
		}
	} else {
		return time.Time{}, ErrInvalidTimestamp
	}

	days := civilToDays(year, mon, day)
	utcSecs := days*86400 + int64(hour)*3600 + int64(min)*60 + int64(sec) - offsetSecs

	return time.Unix(utcSecs, 0).UTC(), nil
}
