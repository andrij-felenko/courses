using System;
using DigitalHomes.ClimateControl.Application;

namespace DigitalHomes.ClimateControl.Controllers;

/// <summary>
/// API-контролер для взаємодії з кліматичною системою Digital Homes.
/// Демонструє контраст між виконанням команд запису (де потрібен домен)
/// та двома альтернативними стратегіями виконання запитів читання.
/// </summary>
public sealed class ClimateController
{
    private readonly PassThroughClimateService _passThroughService;
    private readonly DapperClimateQueries _bypassQueries;

    public ClimateController(
        PassThroughClimateService passThroughService,
        DapperClimateQueries bypassQueries)
    {
        _passThroughService = passThroughService;
        _bypassQueries = bypassQueries;
    }

    /// <summary>
    /// Шлях запису (Command): вимагає обов'язкової участі доменного агрегату Room
    /// для контролю теплового кроку, гістерезису та стану нагрівача.
    /// </summary>
    public void SetTemperature(SetTemperatureCommand command)
    {
        _passThroughService.Handle(command);
    }

    /// <summary>
    /// Шлях читання №1 (Антипатерн Pass-Through Layer):
    /// Проганяє запит дашборду крізь усі шари абстракції, навантажуючи GC.
    /// </summary>
    public ClimateDashboardDto GetDashboardViaPassThrough()
    {
        return _passThroughService.GetClimateDashboard();
    }

    /// <summary>
    /// Шлях читання №2 (CQRS Bypass Channel):
    /// Напряму вичитує оптимізовану проєкцію з бази в DTO через Dapper.
    /// </summary>
    public ClimateDashboardDto GetDashboardViaBypass()
    {
        return _bypassQueries.GetClimateDashboard();
    }
}
