using System.Collections.Concurrent;
using System.Threading.Channels;
using DigitalHomes.TempoBuffer.Models;

namespace DigitalHomes.TempoBuffer.Buffering;

/// <summary>
/// Асинхронна черга команд з обмеженням частоти перемикання силових реле (Throttling / Cooldown).
/// Захищає фізичне обладнання (котли опалення, компресори кондиціонерів, електромагнітні пускачі)
/// від надто частого перемикання через коливання навколо цільової уставки (брязкіт контактів).
/// </summary>
public class ThrottledActuatorQueue : IAsyncDisposable
{
    private readonly TimeSpan _minSwitchInterval;
    private readonly Action<ActuatorCommand>? _hardwareDispatcher;
    private readonly Channel<ActuatorCommand> _channel;
    private readonly ConcurrentDictionary<string, (ActuatorAction Action, DateTime ExecutedUtc)> _lastState = new();
    private readonly Task _workerTask;
    private readonly CancellationTokenSource _cts = new();

    public int DispatchedCount { get; private set; }
    public int SuppressedCount { get; private set; }

    public ThrottledActuatorQueue(TimeSpan? minSwitchInterval = null, Action<ActuatorCommand>? hardwareDispatcher = null)
    {
        _minSwitchInterval = minSwitchInterval ?? TimeSpan.FromSeconds(1);
        _hardwareDispatcher = hardwareDispatcher;
        _channel = Channel.CreateUnbounded<ActuatorCommand>(new UnboundedChannelOptions
        {
            SingleReader = true,
            SingleWriter = false
        });

        _workerTask = Task.Run(ProcessQueueAsync);
    }

    /// <summary>
    /// Ставить команду в чергу на обробку актуатором.
    /// </summary>
    public ValueTask EnqueueAsync(ActuatorCommand command)
    {
        return _channel.Writer.WriteAsync(command);
    }

    private async Task ProcessQueueAsync()
    {
        var reader = _channel.Reader;

        while (await reader.WaitToReadAsync(_cts.Token))
        {
            while (reader.TryRead(out var command))
            {
                var now = DateTime.UtcNow;
                var actuatorId = command.ActuatorId;

                if (_lastState.TryGetValue(actuatorId, out var last))
                {
                    // Якщо реле вже перебуває в цьому стані — команда надлишкова
                    if (last.Action == command.Action)
                    {
                        SuppressedCount++;
                        continue;
                    }

                    // Перевірка обмеження мінімального інтервалу між перемиканнями (cooldown)
                    var elapsed = now - last.ExecutedUtc;
                    if (elapsed < _minSwitchInterval)
                    {
                        // Захист реле: команда відхиляється або гаситься, щоб уникнути пошкодження контактів
                        SuppressedCount++;
                        continue;
                    }
                }

                // Виконання команди на фізичному залізі
                _lastState[actuatorId] = (command.Action, now);
                DispatchedCount++;
                _hardwareDispatcher?.Invoke(command);
            }
        }
    }

    public async ValueTask DisposeAsync()
    {
        _channel.Writer.Complete();
        _cts.Cancel();
        try
        {
            await _workerTask;
        }
        catch (OperationCanceledException)
        {
            // Очікуване завершення фонової задачі
        }
        _cts.Dispose();
    }
}
