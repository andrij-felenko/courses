# Proj Opp Dt Example

```devicetree
cpus {
    cpu@0 {
        compatible = "arm,cortex-a53";
        device_type = "cpu";
        operating-points-v2 = <&cpu_opp_table>;
    };
};

cpu_opp_table: opp_table {
    compatible = "operating-points-v2";
    opp-shared;

    opp-300000000 {
        opp-hz = /bits/ 64 <300000000>;
        opp-microvolt = <900000>;
        clock-latency-ns = <200000>;
    };
    opp-500000000 {
        opp-hz = /bits/ 64 <500000000>;
        opp-microvolt = <1000000>;
        clock-latency-ns = <200000>;
    };
    opp-800000000 {
        opp-hz = /bits/ 64 <800000000>;
        opp-microvolt = <1150000>;
        clock-latency-ns = <200000>;
    };
    opp-1000000000 {
        opp-hz = /bits/ 64 <1000000000>;
        opp-microvolt = <1250000>;
        clock-latency-ns = <200000>;
    };
};
```
