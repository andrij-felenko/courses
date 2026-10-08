using System;
using System.IO;
using CameraInspectionSdk;

public class VideoStreamHandler
{
    public void InitializeStream(CameraDevice camera)
    {
        // Підписка на подію надходження кадру з кільцевого буфера
        camera.FrameReceived += OnFrameReceived;
        camera.StartAcquisition();
    }

    private void OnFrameReceived(object sender, FrameEventArgs args)
    {
        using (FrameBuffer buffer = args.GetBuffer())
        {
            if (buffer.IsCorrupted) return;

            // Конвертація сирого RAW-масиву в колірне зображення
            using (ImageBuffer rgbFrame = buffer.ToRGB24())
            {
                // Накладання метрологічної сітки вимірювання
                rgbFrame.DrawGridOverlay(gridSpacingPx: 50, colorRgb: 0x00FF00);

                // Збереження стиснутого кадру на диск
                rgbFrame.Save("capture_result.jpg", ImageFormat.Jpeg);
            }
        }
    }
}
