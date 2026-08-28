/* Типізоване представлення структур pinctrl у C++20 */
namespace zephyr_pinctrl {

inline constexpr std::array<pinctrl_soc_pin_t, 2> usart1_default_pins = {
    STM32_PINMUX('A', 9, AF7) | STM32_OTYPE_PP | STM32_OSPEED_VHIGH,
    STM32_PINMUX('A', 10, AF7) | STM32_PUPDR_PULLUP,
};

inline constexpr std::array<struct pinctrl_state, 1> usart1_states = {{
    { .id = PINCTRL_STATE_DEFAULT, .pins = usart1_default_pins.data(), .pin_cnt = usart1_default_pins.size() }
}};

} // namespace zephyr_pinctrl
