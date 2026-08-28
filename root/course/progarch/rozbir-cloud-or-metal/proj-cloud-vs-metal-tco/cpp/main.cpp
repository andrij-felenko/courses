#include <iostream>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <limits>

struct WorkloadRequirements {
    double vCpuNeeded;
    double ramGbNeeded;
    double storageTbNeeded;
    double monthlyEgressGb;
    int horizonMonths;
};

struct CloudPricing {
    double pricePerVcpuHour;
    double pricePerRamGbHour;
    double storagePricePerTbMonth;
    double egressPricePerGb;
    double managedServicesFeeMonthly;
};

struct BareMetalPricing {
    double serverCapEx;
    double vCpuPerServer;
    double ramGbPerServer;
    double storageTbPerServer;
    double rackUnitMonthlyFee;
    double powerKwPerHourPrice;
    double serverPowerDrawKw;
    double pueRatio;
    double unmeteredBandwidthMonthlyFee;
    double opsSalaryAllocationMonthly;
};

struct TcoComparisonResult {
    double cloudMonthlyTotal;
    double bareMetalMonthlyTotal;
    double bareMetalCapExTotal;
    double monthlySavings;
    double paybackPeriodMonths;
};

class TcoCalculator {
public:
    static TcoComparisonResult calculate(
        const WorkloadRequirements& req,
        const CloudPricing& cloud,
        const BareMetalPricing& metal)
    {
        constexpr double hoursPerMonth = 730.0;

        // 1. Хмарний OpEx
        double cloudCompute = req.vCpuNeeded * cloud.pricePerVcpuHour * hoursPerMonth +
                             req.ramGbNeeded * cloud.pricePerRamGbHour * hoursPerMonth;
        double cloudStorage = req.storageTbNeeded * cloud.storagePricePerTbMonth;
        double cloudEgress = req.monthlyEgressGb * cloud.egressPricePerGb;
        double cloudMonthlyTotal = cloudCompute + cloudStorage + cloudEgress + cloud.managedServicesFeeMonthly;

        // 2. Bare Metal CapEx + OpEx
        int serversByCpu = static_cast<int>(std::ceil(req.vCpuNeeded / metal.vCpuPerServer));
        int serversByRam = static_cast<int>(std::ceil(req.ramGbNeeded / metal.ramGbPerServer));
        int serversByStorage = static_cast<int>(std::ceil(req.storageTbNeeded / metal.storageTbPerServer));
        int serverCount = std::max({serversByCpu, serversByRam, serversByStorage});

        double totalCapEx = serverCount * metal.serverCapEx;
        double monthlyAmortization = totalCapEx / static_cast<double>(req.horizonMonths);

        double rackFee = serverCount * metal.rackUnitMonthlyFee;
        double kwhUsedMonthly = serverCount * metal.serverPowerDrawKw * hoursPerMonth * metal.pueRatio;
        double powerFee = kwhUsedMonthly * metal.powerKwPerHourPrice;

        double bareMetalMonthlyTotal = monthlyAmortization + rackFee + powerFee +
                                      metal.unmeteredBandwidthMonthlyFee +
                                      metal.opsSalaryAllocationMonthly;

        double monthlySavings = cloudMonthlyTotal - bareMetalMonthlyTotal;
        double paybackPeriodMonths = (monthlySavings > 0.0) 
            ? (totalCapEx / monthlySavings) 
            : std::numeric_limits<double>::infinity();

        return TcoComparisonResult{
            cloudMonthlyTotal,
            bareMetalMonthlyTotal,
            totalCapEx,
            monthlySavings,
            paybackPeriodMonths
        };
    }
};
