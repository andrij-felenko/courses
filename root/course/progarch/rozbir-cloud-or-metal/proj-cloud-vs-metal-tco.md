# ⚙️ Модель і розрахунок TCO: Хмара проти заліза в коді

Для обґрунтованого вибору між публічною хмарою (AWS, GCP, Azure) та власною інфраструктурою (Co-location / Bare Metal) потрібен числовий калькулятор сукупної вартості володіння (TCO — Total Cost of Ownership). Просте порівняння місячної ціни інстансу та вартості сервера на поличці є помилковим, оскільки воно ігнорує амортизацію, споживання електрики, коефіцієнт PUE дата-центру, вартість мережевих портів, egress-трафіку та додаткове навантаження на інженерну команду.

Нижче розроблено алгоритм TCO, який зводить усі ці параметри до єдиної щомісячної вартості та розраховує термін окупності капітальних інвестицій у залізо.

## 1. Детальний аналіз параметрів інфраструктурної моделі

Модель порівнює дві незалежні фінансові траєкторії на заданому часовому горизонті (за замовчуванням 36 місяців). Для цього враховуються три класи параметрів:

### А. Потреби навантаження (Workload Requirements)
- **`vCpuNeeded`**: Загальна кількість віртуальних ядер процесора, необхідних для виконання застосунків. Важливо враховувати, що у публічних хмарах одне vCPU зазвичай дорівнює одному потоку (Hyper-Thread) фізичного ядра, тоді як на Bare Metal фізичне ядро дає 2 повноцінні потоки без оверквотингу гіпервізора.
- **`ramGbNeeded`**: Сукупна оперативна пам'ять (ОЗУ) у Гігабайтах. У хмарах співвідношення vCPU до RAM жорстко обмежене типом інстансу (наприклад, 1:4 у General Purpose або 1:8 у Memory Optimized). На Bare Metal сервер можна укомплектувати будь-яким обсягом RAM під вимоги продукту.
- **`storageTbNeeded`**: Потрібний обсяг дискового сховища у Терабайтах. У хмарах диски EBS вимагають окремої оплати за розмір та гарантовану швидкість (IOPS). На Bare Metal локальні NVMe-накопичувачі PCIe 4.0/5.0 надають сотні тисяч IOPS за замовчуванням без додаткової націнки.
- **`monthlyEgressGb`**: Щомісячний обсяг вихідного мережевого трафіку назовні в інтернет або до інших ЦОД.
- **`horizonMonths`**: Термін розрахунку TCO та амортизації обладнання (типово 36 або 60 місяців).

### Б. Хмарний кошторис (Cloud Pricing Structure)
- **`pricePerVcpuHour`** та **`pricePerRamGbHour`**: Погодинні тарифні сітки оренди обчислень. При розрахунку 730 годин на місяць навіть дрібні центі складаються у великі суми.
- **`storagePricePerTbMonth`**: Базова ставка оренди Гігабайта блокового або об'єктного сховища.
- **`egressPricePerGb`**: Прогресивний або фіксований тариф виводу трафіку (типово \$0.08–\$0.12 за ГБ для перших десятків ТБ).
- **`managedServicesFeeMonthly`**: Додаткові фіксовані націнки за керовані сервіси (RDS, Managed Kubernetes EKS/GKE, CloudWatch logs, NAT Gateways).

### В. Кошторис Bare Metal та Co-location
- **`serverCapEx`**: Вартість закупівлі одного сервера в повній конфігурації (корпус, материнська плата, 2 процесори, ОЗУ, NVMe, мережеві карти, блочні БЖ).
- **`vCpuPerServer`**, **`ramGbPerServer`**, **`storageTbPerServer`**: Паспортні ресурси одного фізичного сервера.
- **`rackUnitMonthlyFee`**: Оренда юніта (1U) у стійці дата-центру з дубльованим живленням.
- **`powerKwPerHourPrice`**: Вартість кіловат-години електроенергії у дата-центрі.
- **`serverPowerDrawKw`**: Середнє споживання електроенергії одним сервером під навантаженням (типово 0.4–0.8 кВт для 2U сервера).
- **`pueRatio`**: Коефіцієнт ефективності використання енергії (Power Usage Effectiveness) ЦОД. PUE = 1.25 означає, що на кожен 1 кВт споживання сервера дата-центр витрачає 0.25 кВт на охолодження та трансформацію.
- **`unmeteredBandwidthMonthlyFee`**: Фіксована місячна вартість виділеного безлімітного порту трафіку (10 Gbps або 40 Gbps).
- **`opsSalaryAllocationMonthly`**: Виділена частка місячного фонду оплати праці системного адміністратора чи DevOps-інженера на обслуговування даного кластера.

## 2. Математичний алгоритм розрахунку TCO

Модель обчислює дві незалежні фінансові траєкторії на заданому часовому горизонті (за замовчуванням 36 місяців):

1. **Хмарний OpEx (`cloudMonthlyTotal`)**:
   - `cloudCompute = (vCpuNeeded · pricePerVcpuHour + ramGbNeeded · pricePerRamGbHour) · 730`
   - `cloudStorage = storageTbNeeded · storagePricePerTbMonth`
   - `cloudEgress = monthlyEgressGb · egressPricePerGb`
   - `cloudMonthlyTotal = cloudCompute + cloudStorage + cloudEgress + managedServicesFeeMonthly`

2. **Bare Metal CapEx + OpEx (`bareMetalMonthlyTotal`)**:
   - `serverCount = max(ceil(vCpuNeeded / vCpuPerServer), ceil(ramGbNeeded / ramGbPerServer), ceil(storageTbNeeded / storageTbPerServer))`
   - `totalCapEx = serverCount · serverCapEx`
   - `monthlyAmortization = totalCapEx / horizonMonths`
   - `powerFee = serverCount · serverPowerDrawKw · 730 · pueRatio · powerKwPerHourPrice`
   - `bareMetalMonthlyTotal = monthlyAmortization + (serverCount · rackUnitMonthlyFee) + powerFee + unmeteredBandwidthMonthlyFee + opsSalaryAllocationMonthly`

3. **Термін окупності CapEx (`paybackPeriodMonths`)**:
   - `monthlySavings = cloudMonthlyTotal - bareMetalMonthlyTotal`
   - `paybackPeriodMonths = totalCapEx / monthlySavings`

## 3. Реалізація калькулятора мовами TypeScript та C++

Наведена нижче програма приймає вимоги до інфраструктури, хмарні тарифи та параметри розміщення Bare Metal, видаючи розраховані суми витрат та термін повернення інвестицій.

:::tabs
```ts
export interface WorkloadRequirements {
  vCpuNeeded: number;
  ramGbNeeded: number;
  storageTbNeeded: number;
  monthlyEgressGb: number;
  horizonMonths: number;
}

export interface CloudPricing {
  pricePerVcpuHour: number;
  pricePerRamGbHour: number;
  storagePricePerTbMonth: number;
  egressPricePerGb: number;
  managedServicesFeeMonthly: number;
}

export interface BareMetalPricing {
  serverCapEx: number;             // вартість одного сервера (CapEx)
  vCpuPerServer: number;
  ramGbPerServer: number;
  storageTbPerServer: number;
  rackUnitMonthlyFee: number;       // оренда юніта в ЦОД
  powerKwPerHourPrice: number;       // вартість кВт·год
  serverPowerDrawKw: number;        // споживання одного сервера в кВт
  pueRatio: number;                 // коефіцієнт PUE (наприклад 1.25)
  unmeteredBandwidthMonthlyFee: number; // плоский 10G порт
  opsSalaryAllocationMonthly: number; // частка зарплати інженера
}

export interface TcoComparisonResult {
  cloudMonthlyTotal: number;
  bareMetalMonthlyTotal: number;
  bareMetalCapExTotal: number;
  monthlySavings: number;
  paybackPeriodMonths: number;
}

export function calculateTco(
  req: WorkloadRequirements,
  cloud: CloudPricing,
  metal: BareMetalPricing
): TcoComparisonResult {
  const hoursPerMonth = 730;

  // 1. Хмарні витрати
  const cloudCompute = req.vCpuNeeded * cloud.pricePerVcpuHour * hoursPerMonth +
                       req.ramGbNeeded * cloud.pricePerRamGbHour * hoursPerMonth;
  const cloudStorage = req.storageTbNeeded * cloud.storagePricePerTbMonth;
  const cloudEgress = req.monthlyEgressGb * cloud.egressPricePerGb;
  const cloudMonthlyTotal = cloudCompute + cloudStorage + cloudEgress + cloud.managedServicesFeeMonthly;

  // 2. Bare Metal витрати
  const serversByCpu = Math.ceil(req.vCpuNeeded / metal.vCpuPerServer);
  const serversByRam = Math.ceil(req.ramGbNeeded / metal.ramGbPerServer);
  const serversByStorage = Math.ceil(req.storageTbNeeded / metal.storageTbPerServer);
  const serverCount = Math.max(serversByCpu, serversByRam, serversByStorage);

  const totalCapEx = serverCount * metal.serverCapEx;
  const monthlyAmortization = totalCapEx / req.horizonMonths;

  const rackFee = serverCount * metal.rackUnitMonthlyFee;
  const kwhUsedMonthly = serverCount * metal.serverPowerDrawKw * hoursPerMonth * metal.pueRatio;
  const powerFee = kwhUsedMonthly * metal.powerKwPerHourPrice;
  
  const bareMetalMonthlyTotal = monthlyAmortization + rackFee + powerFee + 
                                metal.unmeteredBandwidthMonthlyFee + 
                                metal.opsSalaryAllocationMonthly;

  const monthlySavings = cloudMonthlyTotal - bareMetalMonthlyTotal;
  const paybackPeriodMonths = monthlySavings > 0 ? totalCapEx / monthlySavings : Infinity;

  return {
    cloudMonthlyTotal,
    bareMetalMonthlyTotal,
    bareMetalCapExTotal: totalCapEx,
    monthlySavings,
    paybackPeriodMonths
  };
}
```
```cpp
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
```
:::

## 4. Аналіз чутливості та практичний приклад

Розглянемо практичний розрахунок для компанії середнього масштабу (профіль 37signals / Basecamp):

- **Потреба у ресурсах**: 256 vCPU, 1024 ГБ RAM, 50 ТБ NVMe сховища та 80 000 ГБ Egress-трафіку на місяць. Часовий горизонт — 36 місяців.
- **Хмарний тариф (AWS On-Demand / Managed)**: \$0.035 за vCPU/годину, \$0.0045 за ГБ RAM/годину, \$0.09 за ГБ Egress. Хмарний рахунок складе близько **\$22 800 на місяць**.
- **Bare Metal розрахунок**: Потрібно 4 класичні сервери Dell 2U (по 64 ядра, 256 ГБ RAM, 15 ТБ NVMe кожен). Вартість сервера — \$11 000 (загальний CapEx = \$44 000). Амортизація за 36 місяців — \$1 222/місяць.
- **Оренда стійок та електрика**: 8U у ЦОД (\$400), електрика при PUE 1.25 (\$550), 10G unmetered порт (\$1 200), виділений біт адміністрування (\$1 500). Разом місячні витрати на Bare Metal складатимуть близько **\$4 872 на місяць** (із урахуванням амортизації заліза).

Щомісячна чиста економія становить **\$17 928**. При загальному CapEx у \$44 000 початкові інвестиції у купівлю заліза повністю окупаються за **2.45 місяці** (менш ніж за чверть року).

## 5. Інженерні пастки та крайні випадки при розрахунку TCO

Під час побудови власного калькулятора слід берегтися трьох найчастіших помилок:

1. **Нехтування запасними частинами (Spares & Buffer)**: Купівля рівно `N` серверів не враховує апаратних виходів з ладу. Рекомендовано додавати 10%–15% залізо-буфера (Cold Standby) до капітальних витрат.
2. **Недооцінка зносу накопичувачів (NVMe Wear-out)**: При інтенсивному записі диски NVMe зношуються за 2–3 роки. Термін життя дисків має враховуватись у планових OpEx витратах на запчастини.
3. **Ілюзія відсутності адміністрування у хмарі**: Сервіси AWS чи GCP зменшують ручну роботу, але не обнуляють її. Налаштування IAM, Security Groups, Terraform-скриптів та моніторингу все одно потребує роботи DevOps-інженерів.
4. **Сплески навантаження (Peak vs Baseline)**: Якщо 90% часу вам потрібно 4 сервери, а 10% часу — 40 серверів, рішення на Bare Metal вимагатиме закупівлі 40 серверів, які більшу частину часу простоюватимуть. У такому разі оптимальним є **гібридний підхід**: baseline у 4 сервери на Bare Metal, а пікові сплески на 36 серверів розвертаються у хмарі через автоскейлінг (Auto-scaling groups).
