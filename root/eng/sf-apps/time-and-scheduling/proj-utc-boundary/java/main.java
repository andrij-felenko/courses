// Межа: настінний час ↔ мить. java.time, без залежностей.
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.time.zone.ZoneRules;
import java.util.List;

enum Kind { EXACT, GAP, AMBIGUOUS }

record Resolved(Instant instant, Kind kind) {}

final class Boundary {
    private static final DateTimeFormatter OUT =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm XXX");

    /** wall — настінний час без зони. Каже, скільки митей йому відповідало. */
    static Resolved resolveLocal(LocalDateTime wall, String zone) {
        ZoneRules rules = ZoneId.of(zone).getRules();
        List<ZoneOffset> valid = rules.getValidOffsets(wall);
        if (valid.size() == 1)
            return new Resolved(wall.toInstant(valid.get(0)), Kind.EXACT);
        // два дійсні зсуви — перший у списку той, що діяв ДО переходу
        if (valid.size() == 2)
            return new Resolved(wall.toInstant(valid.get(0)), Kind.AMBIGUOUS);
        // порожньо — діра; ZonedDateTime.of сам зсуває вперед на її довжину
        return new Resolved(ZonedDateTime.of(wall, ZoneId.of(zone)).toInstant(), Kind.GAP);
    }

    /** Мить → напис у зоні читача: «2026-10-25 03:30 +03:00». */
    static String formatInZone(Instant instant, String zone) {
        return instant.atZone(ZoneId.of(zone)).format(OUT);
    }

    /** Півзакритий проміжок [від, до) — доба користувача на осі митей. */
    static Instant[] dayBounds(LocalDate day, String zone) {
        return new Instant[] {
            resolveLocal(day.atStartOfDay(), zone).instant(),
            resolveLocal(day.plusDays(1).atStartOfDay(), zone).instant()
        };
    }
}
