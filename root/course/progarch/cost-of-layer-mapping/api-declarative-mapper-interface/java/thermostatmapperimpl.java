// Контракт мапера мовою Java, який пише розробник
package com.digitalhomes.climate.mapper;

import com.digitalhomes.climate.dto.ThermostatResponseDto;
import com.digitalhomes.climate.model.ThermostatEntity;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.factory.Mappers;

@Mapper
public interface ThermostatMapper {
    ThermostatMapper INSTANCE = Mappers.getMapper(ThermostatMapper.class);

    @Mapping(source = "roomIdentifier", target = "roomId")
    @Mapping(source = "targetTempCelsius", target = "targetTemperature")
    ThermostatResponseDto toResponseDto(ThermostatEntity entity);
}

// Процедурний клас, який автоматично згенерував MapStruct під час збірки
package com.digitalhomes.climate.mapper;

import com.digitalhomes.climate.dto.ThermostatResponseDto;
import com.digitalhomes.climate.model.ThermostatEntity;

public class ThermostatMapperImpl implements ThermostatMapper {
    @Override
    public ThermostatResponseDto toResponseDto(ThermostatEntity entity) {
        if (entity == null) {
            return null;
        }

        ThermostatResponseDto dto = new ThermostatResponseDto();
        dto.setRoomId(entity.getRoomIdentifier());
        dto.setTargetTemperature(entity.getTargetTempCelsius());
        dto.setCurrentTemperature(entity.getCurrentTemperature());
        dto.setActive(entity.isActive());

        return dto;
    }
}
