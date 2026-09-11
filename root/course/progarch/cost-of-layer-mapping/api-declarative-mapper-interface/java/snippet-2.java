// Конфігурація суворого мапера для Spring Boot (MapStruct)
package com.digitalhomes.climate.mapper;

import com.digitalhomes.climate.dto.ThermostatResponseDto;
import com.digitalhomes.climate.model.ThermostatEntity;
import org.mapstruct.InjectionStrategy;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.NullValueMappingStrategy;
import org.mapstruct.ReportingPolicy;

@Mapper(
    componentModel = "spring",
    injectionStrategy = InjectionStrategy.CONSTRUCTOR,
    unmappedTargetPolicy = ReportingPolicy.ERROR,
    unmappedSourcePolicy = ReportingPolicy.WARN,
    nullValueMappingStrategy = NullValueMappingStrategy.RETURN_NULL
)
public interface ThermostatMapper {

    @Mapping(source = "roomIdentifier", target = "roomId")
    @Mapping(source = "targetTempCelsius", target = "targetTemperature")
    @Mapping(target = "internalRevision", ignore = true) // Явно оголошено, що поле не йде в DTO
    ThermostatResponseDto toDto(ThermostatEntity entity);
}
