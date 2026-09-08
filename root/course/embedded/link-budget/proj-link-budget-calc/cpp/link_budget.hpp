#pragma once

#include <string>
#include <stdexcept>

namespace rf {

struct LinkParameters {
    double freq_mhz = 868.0;
    double distance_km = 5.0;
    double tx_power_dbm = 14.0;
    double tx_gain_dbi = 2.15;
    double tx_loss_db = 0.5;
    double rx_gain_dbi = 2.15;
    double rx_loss_db = 0.5;
    double rx_sensitivity_dbm = -125.0;
};

struct LinkReport {
    double fspl_db = 0.0;
    double eirp_dbm = 0.0;
    double prx_dbm = 0.0;
    double margin_db = 0.0;
    bool is_reliable = false;

    [[nodiscard]] std::string format() const;
};

class LinkBudget {
public:
    explicit LinkBudget(LinkParameters params);

    [[nodiscard]] LinkReport evaluate() const;
    [[nodiscard]] const LinkParameters& params() const noexcept { return params_; }

    void set_distance(double km);
    void set_tx_power(double dbm);

private:
    void validate() const;
    LinkParameters params_;
};

} // namespace rf
