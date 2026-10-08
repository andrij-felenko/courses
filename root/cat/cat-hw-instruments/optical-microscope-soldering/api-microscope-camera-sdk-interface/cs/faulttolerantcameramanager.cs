using System;
using System.Threading;
using System.Threading.Tasks;
using CameraInspectionSdk;

public class FaultTolerantCameraManager
{
    private CameraDevice _camera;

    public void StartWatchdog()
    {
        Task.Run(() =>
        {
            while (true) {
                Thread.Sleep(1000);
                if (_camera != null && !_camera.IsHeartbeatAlive()) {
                    Console.WriteLine("Критичний збій: втрата серцебиття. Відновлення...");
                    ReconstructSession();
                }
            }
        });
    }

    private void ReconstructSession()
    {
        _camera?.Dispose();
        _camera = null;

        while (true) {
            try {
                var devices = CameraSystem.EnumerateDevices();
                if (devices.Length > 0) {
                    _camera = CameraSystem.ConnectDevice(devices[0].DeviceId);
                    _camera.SetProperty(PropertyId.ExposureTimeUs, 2500.0);
                    _camera.StartAcquisition();
                    Console.WriteLine("Сесію камери успішно реконструйовано.");
                    break;
                }
            } catch {
                // Затримка перед повторною спробою
            }
            Thread.Sleep(2000);
        }
    }
}
