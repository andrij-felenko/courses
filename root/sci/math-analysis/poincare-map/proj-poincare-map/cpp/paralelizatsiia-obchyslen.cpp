#include <execution>
#include <algorithm>

std::vector<double> lambda_values = generate_parameter_grid(0.1, 0.5, 1000);
std::vector<std::vector<State>> bif_diagram(lambda_values.size());

std::transform(std::execution::par, 
               lambda_values.begin(), lambda_values.end(), 
               bif_diagram.begin(),
               [](double lambda) {
                   SystemParameters params{ .gamma = 0.2, .f0 = lambda, .omega = 1.0 };
                   DuffingSystem sys(params);
                   SectionCollector collector(sys);
                   auto res = collector.compute_section({0.1, 0.0}, 1000, 200, 500);
                   return res ? *res : std::vector<State>{};
               });
