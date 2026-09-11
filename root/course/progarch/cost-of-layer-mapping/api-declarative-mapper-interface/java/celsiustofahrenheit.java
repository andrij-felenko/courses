// Мапер зі спеціалізованими конвертерами мовою Java (MapStruct)
package com.digitalhomes.climate.mapper;

import com.digitalhomes.climate.dto.ThermostatResponseDto;
import com.digitalhomes.climate.model.ThermostatEntity;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;
import org.mapstruct.ReportingPolicy;

@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.ERROR)
public interface ThermostatDetailMapper {

    @Mapping(source = "roomIdentifier", target = "roomId")
    @Mapping(source = "targetTempCelsius", target = "targetTemperatureFahrenheit", qualifiedByName = "celsiusToFahrenheit")
    @Mapping(target = "firmwareRevision", ignore = true)
    ThermostatResponseDto toDto(ThermostatEntity entity);

    @Named("celsiusToFahrenheit")
    default int celsiusToFahrenheit(double celsius) {
        return (int) Math.round(celsius * 1.8 + 32);
    }
}
