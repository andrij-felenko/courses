using System;
using CameraInspectionSdk;

class Program
{
    static void Main()
    {
        // Ініціалізація ядра SDK
        CameraSystem.Initialize();

        try
        {
            // Перелік підключених інспекційних камер
            DeviceInfo[] devices = CameraSystem.EnumerateDevices();
            if (devices.Length == 0)
            {
                Console.WriteLine("Пристрої контролю відсутні на шині.");
                return;
            }

            // Відкриття підключення до камери через керуючий об'єкт
            using (CameraDevice camera = CameraSystem.ConnectDevice(devices[0].DeviceId))
            {
                Console.WriteLine($"Успішна ініціалізація: {camera.ModelName}");
                camera.SetTransportProperty(PropertyId.StreamPacketSize, 9000);

                // Сесія активна для зчитування параметрів
            } // Автоматичний виклику Dispose(), закриття хендла та звільнення буферів
        }
        catch (CameraSdkException ex)
        {
            Console.WriteLine($"Помилка сесії камери: {ex.Message}");
        }
        finally
        {
            CameraSystem.Shutdown();
        }
    }
}
