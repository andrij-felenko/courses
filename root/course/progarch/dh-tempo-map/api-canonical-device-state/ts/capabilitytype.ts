// Канонічні типи можливостей платформи Digital Homes
export type CapabilityType =
  | 'on_off'
  | 'brightness'
  | 'color_temperature'
  | 'current_temperature'
  | 'contact_sensor'
  | 'power_meter';

// Специфікація значень кожної можливості в нормалізованих одиницях SI
export interface OnOffCapability {
  type: 'on_off';
  on: boolean;
}

export interface BrightnessCapability {
  type: 'brightness';
  // Нормалізована частка від 0.0 (вимкнено) до 1.0 (максимальна яскравість)
  level: number;
}

export interface ColorTemperatureCapability {
  type: 'color_temperature';
  // Колірна температура у Кельвінах (K), наприклад 2700..6500
  kelvin: number;
}

export interface CurrentTemperatureCapability {
  type: 'current_temperature';
  // Температура у градусах Цельсія (°C)
  celsius: number;
}

export interface ContactSensorCapability {
  type: 'contact_sensor';
  state: 'open' | 'closed';
}

export interface PowerMeterCapability {
  type: 'power_meter';
  // Миттєва активна потужність у ватах (W)
  watts: number;
}

export type CapabilityState =
  | OnOffCapability
  | BrightnessCapability
  | ColorTemperatureCapability
  | CurrentTemperatureCapability
  | ContactSensorCapability
  | PowerMeterCapability;

// Моментальний знімок стану пристрою, що повертається клієнтам
export interface DeviceStateSnapshot {
  deviceId: string;
  schemaVersion: number;
  // Часова мітка останнього оновлення у форматі ISO 8601 UTC
  updatedAt: string;
  // Прапорець доступності фізичного пристрою на радіошині
  online: boolean;
  // Словник активних можливостей пристрою за їхніми ідентифікаторами
  capabilities: {
    on_off?: OnOffCapability;
    brightness?: BrightnessCapability;
    color_temperature?: ColorTemperatureCapability;
    current_temperature?: CurrentTemperatureCapability;
    contact_sensor?: ContactSensorCapability;
    power_meter?: PowerMeterCapability;
  };
}

// Приклад адаптера: трансляція сирих атрибутів Zigbee ZCL у канонічний знімок
export function mapZigbeeToCanonical(
  deviceId: string,
  zclClusters: {
    onOffCluster?: { onOff: boolean };
    levelCluster?: { currentLevel: number }; // діапазон 0..254
    tempCluster?: { measuredValue: number };  // значення в сотих °C (2150 = 21.50 °C)
  },
  isOnline: boolean
): DeviceStateSnapshot {
  const capabilities: DeviceStateSnapshot['capabilities'] = {};

  if (zclClusters.onOffCluster) {
    capabilities.on_off = {
      type: 'on_off',
      on: zclClusters.onOffCluster.onOff,
    };
  }

  if (zclClusters.levelCluster) {
    // Нормалізуємо апаратний діапазон 0..254 у частку 0.0..1.0
    const rawLevel = zclClusters.levelCluster.currentLevel;
    const clampedLevel = Math.max(0, Math.min(254, rawLevel));
    capabilities.brightness = {
      type: 'brightness',
      level: Number((clampedLevel / 254).toFixed(3)),
    };
  }

  if (zclClusters.tempCluster) {
    // Перетворюємо соті частки у реальні градуси Цельсія
    capabilities.current_temperature = {
      type: 'current_temperature',
      celsius: zclClusters.tempCluster.measuredValue / 100,
    };
  }

  return {
    deviceId: deviceId,
    schemaVersion: 1,
    updatedAt: new Date().toISOString(),
    online: isOnline,
    capabilities: capabilities,
  };
}

// Приклад адаптера: трансляція сирих даних протоколу Matter у той самий контракт
export function mapMatterToCanonical(
  deviceId: string,
  matterAttributes: {
    lightingOnOff?: boolean;
    lightingLevel?: number; // діапазон Matter 1..254
  },
  isOnline: boolean
): DeviceStateSnapshot {
  const capabilities: DeviceStateSnapshot['capabilities'] = {};

  if (matterAttributes.lightingOnOff !== undefined) {
    capabilities.on_off = {
      type: 'on_off',
      on: matterAttributes.lightingOnOff,
    };
  }

  if (matterAttributes.lightingLevel !== undefined) {
    // В Matter 1 відповідає мінімальній яскравості, 254 — максимальній
    const raw = matterAttributes.lightingLevel;
    const normalized = Math.max(0, Math.min(1, (raw - 1) / 253));
    capabilities.brightness = {
      type: 'brightness',
      level: Number(normalized.toFixed(3)),
    };
  }

  return {
    deviceId: deviceId,
    schemaVersion: 1,
    updatedAt: new Date().toISOString(),
    online: isOnline,
    capabilities: capabilities,
  };
}
