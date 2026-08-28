from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from datetime import datetime

class IDeviceRegistryModule(ABC):
    @abstractmethod
    def get_device(self, device_id: str) -> DeviceDTO | None:
        """Повертає знімок стану пристрою за його унікальним ідентифікатором.
        
        Параметри:
          - device_id: Унікальний GUID пристрою у форматі рядка (36 символів).
        Повертає:
          - DeviceDTO: Заморожений знімок стану пристрою.
          - None: Якщо пристрій з таким ідентифікатором відсутній у реєстрі.
        Винятки:
          - DeviceRegistryError: При виникненні внутрішньої помилки доступу до даних.
        """
        pass

    @abstractmethod
    def list_home_devices(self, home_id: str, device_type: str | None = None) -> list[DeviceDTO]:
        """Повертає перелік усіх пристроїв, прикріплених до конкретного дому.
        
        Параметри:
          - home_id: Унікальний GUID дому.
          - device_type: (Опціонально) Рядковий фільтр за типом пристрою 
                         ('sensor', 'actuator', 'hub', 'camera').
        Повертає:
          - Список об'єктів DeviceDTO. Якщо пристроїв немає — повертає порожній список [].
        """
        pass

    @abstractmethod
    def update_desired_state(self, device_id: str, desired_payload: dict[str, Any], updated_by_user_id: str) -> bool:
        """Оновлює бажаний стан пристрою (Desired State) у Device Shadow.
        
        Цей метод використовується модулем автоматизації або API-контролерами для відправки 
        команд пристрою (наприклад, увімкнути реле, змінити цільову температуру).
        
        Параметри:
          - device_id: GUID пристрою.
          - desired_payload: Словник ключ-значення з новими цільовими параметрами.
          - updated_by_user_id: GUID користувача або ідентифікатор 'system_automation'.
        Повертає:
          - True, якщо бажаний стан успішно оновлено та згенеровано дельта-подію.
        Винятки:
          - DeviceNotFoundError: Якщо пристрій відсутній у базі.
          - InvalidStatePayloadError: Якщо параметри payload не відповідають схемі пристрою.
        """
        pass
