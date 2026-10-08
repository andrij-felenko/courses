using System;
using CameraInspectionSdk;

public static class SensorConfigurator
{
    public static void ApplyInspectionSettings(CameraDevice camera)
    {
        // Конфігурування часових та підсилювальних параметрів
        camera.SetProperty(PropertyId.ExposureTimeUs, 2500.0);
        camera.SetProperty(PropertyId.GainDb, 6.0);

        // Налаштування суб-вікна ROI
        camera.SetRegionOfInterest(new ImageRectangle(128, 128, 1024, 768));

        // Конфігурування апаратного суммування елементів матриці
        camera.SetBinning(BinningMode.Binning2x2);

        // Формування масиву нелінійної корекції LUT
        ushort[] lutData = new ushort[4096];
        for (int i = 0; i < 4096; i++)
        {
            double val = i / 4095.0;
            lutData[i] = (ushort)(Math.Sqrt(val) * 4095.0);
        }
        camera.WriteLookUpTable(lutData);
    }
}
