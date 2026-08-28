import { rrulestr } from "rrule";

// DTSTART входить у той самий текст: правило без нього неповне
const rule = rrulestr(
  "DTSTART;TZID=Europe/Kyiv:20260115T090000\n" +
  "RRULE:FREQ=MONTHLY;BYMONTHDAY=15,30;COUNT=5",
);

rule.all();                        // усі п'ять митей
rule.after(new Date(), true);      // найближча після «зараз»
rule.between(from, to);            // усе у вікні [from, to]
rule.toString();                   // назад у рядок RFC 5545
