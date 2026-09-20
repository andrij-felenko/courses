// Сценарій регулювання мікроклімату в доменному ядрі
public class RegulateClimateScenario {
    private final ClimateZonePort climatePort;

    public void execute(Temperature targetTemp) {
        // Виклик порту з реляційним критерієм, прив'язаним до стовпчика таблиці
        List<ClimateZone> coldZones = climatePort.find(
            Criteria.where("current_temp").lessThan(targetTemp.celsius())
        );

        for (ClimateZone zone : coldZones) {
            zone.activateHeating();
        }
    }
}
