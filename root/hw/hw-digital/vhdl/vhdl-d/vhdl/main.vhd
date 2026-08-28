library IEEE;
use IEEE.std_logic_1164.all;      -- std_logic та його 9 значень
use IEEE.numeric_std.all;         -- арифметика над векторами

entity counter is
    port ( clk : in  std_logic;                      -- такт
           rst : in  std_logic;                      -- скидання
           q   : out std_logic_vector(7 downto 0) ); -- 8-бітний вихід
end entity;

architecture rtl of counter is
    signal cnt : unsigned(7 downto 0) := (others => '0');
begin
    process (clk)                        -- реагує на зміну clk
    begin
        if rising_edge(clk) then         -- саме на ФРОНТІ такту
            if rst = '1' then
                cnt <= (others => '0');  -- скинути в нуль
            else
                cnt <= cnt + 1;          -- інакше — на одиницю більше
            end if;
        end if;
    end process;
    q <= std_logic_vector(cnt);          -- вивести назовні
end architecture;
