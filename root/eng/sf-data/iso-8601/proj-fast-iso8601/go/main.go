package iso8601

import (
	"errors"
	"time"
)

var errInvalidFormat = errors.New("invalid iso8601 string")

// DaysFromCivil обчислює кількість днів від 1970-01-01 без алокацій
func daysFromCivil(y int, m, d uint) int64 {
	if m <= 2 {
		y--
	}
	era := y / 400
	if y < 0 {
		era = (y - 399) / 400
	}
	yoe := uint(y - era*400)
	var monthOffset uint = m + 9
	if m > 2 {
		monthOffset = m - 3
	}
	doy := (153*monthOffset+2)/5 + d - 1
	doe := yoe*365 + yoe/4 - yoe/100 + doy
	return int64(era)*146097 + int64(doe) - 719468
}

// ParseFast здійснює нуль-алокаційний розбір мітки часу
func ParseFast(s string) (time.Time, error) {
	if len(s) < 20 {
		return time.Time{}, errInvalidFormat
	}
	if s[4] != '-' || s[7] != '-' || (s[10] != 'T' && s[10] != ' ') ||
		s[13] != ':' || s[16] != ':' {
		return time.Time{}, errInvalidFormat
	}

	year := int(uint(s[0])*1000 + uint(s[1])*100 + uint(s[2])*10 + uint(s[3]) - 53328)
	month := uint(s[5])*10 + uint(s[6]) - 528
	day := uint(s[8])*10 + uint(s[9]) - 528
	hour := uint(s[11])*10 + uint(s[12]) - 528
	min := uint(s[14])*10 + uint(s[15]) - 528
	sec := uint(s[17])*10 + uint(s[18]) - 528

	if month < 1 || month > 12 || day < 1 || day > 31 || hour > 23 || min > 59 || sec > 60 {
		return time.Time{}, errInvalidFormat
	}
	if sec == 60 {
		sec = 59
	}

	idx := 19
	var nanos int
	if idx < len(s) && (s[idx] == '.' || s[idx] == ',') {
		idx++
		mult := 100000000
		for idx < len(s) && s[idx] >= '0' && s[idx] <= '9' {
			if mult > 0 {
				nanos += int(s[idx]-'0') * mult
				mult /= 10
			}
			idx++
		}
	}

	var offsetSecs int
	if idx < len(s) {
		if s[idx] == 'Z' || s[idx] == 'z' {
			offsetSecs = 0
		} else if (s[idx] == '+' || s[idx] == '-') && len(s)-idx >= 6 {
			offH := int(uint(s[idx+1])*10 + uint(s[idx+2]) - 528)
			offM := int(uint(s[idx+4])*10 + uint(s[idx+5]) - 528)
			offsetSecs = offH*3600 + offM*60
			if s[idx] == '-' {
				offsetSecs = -offsetSecs
			}
		}
	}

	days := daysFromCivil(year, month, day)
	utcSecs := days*86400 + int64(hour)*3600 + int64(min)*60 + int64(sec) - int64(offsetSecs)

	return time.Unix(utcSecs, int64(nanos)).UTC(), nil
}
