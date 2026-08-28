#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Повнофункціональний генератор заголовочних файлів C99 та C++20 зі специфікацій CMSIS-SVD 1.3.
Підтримує розрахунок прогалин, derivedFrom, бітові маски, enum class та static_assert.
"""

import sys
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class EnumValue:
    name: str
    value: int
    description: str = ""


@dataclass
class BitField:
    name: str
    bit_offset: int
    bit_width: int
    access: str = "read-write"
    description: str = ""
    enums: List[EnumValue] = field(default_factory=list)

    @property
    def mask(self) -> int:
        return ((1 << self.bit_width) - 1) << self.bit_offset


@dataclass
class Register:
    name: str
    address_offset: int
    size: int = 32  # у бітах
    access: str = "read-write"
    reset_value: int = 0
    reset_mask: int = 0xFFFFFFFF
    description: str = ""
    modified_write: Optional[str] = None
    read_action: Optional[str] = None
    fields: List[BitField] = field(default_factory=list)


@dataclass
class Interrupt:
    name: str
    value: int
    description: str = ""


@dataclass
class Peripheral:
    name: str
    base_address: int
    group_name: str = ""
    header_struct_name: str = ""
    description: str = ""
    derived_from: Optional[str] = None
    interrupts: List[Interrupt] = field(default_factory=list)
    registers: List[Register] = field(default_factory=list)


@dataclass
class Device:
    name: str
    version: str = "1.0"
    description: str = ""
    cpu_name: str = "CM4"
    nvic_prio_bits: int = 4
    peripherals: Dict[str, Peripheral] = field(default_factory=dict)


class SvdParser:
    """Синтаксичний аналізатор XML CMSIS-SVD із підтримкою нормалізації полів."""

    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.tree = ET.parse(xml_path)
        self.root = self.tree.getroot()

    def parse(self) -> Device:
        dev_name = self._get_text(self.root, "name", "UnknownDevice")
        dev_ver = self._get_text(self.root, "version", "1.0")
        dev_desc = self._get_text(self.root, "description", "")

        cpu_elem = self.root.find("cpu")
        cpu_name = self._get_text(cpu_elem, "name", "CM4") if cpu_elem is not None else "CM4"
        nvic_bits = int(self._get_text(cpu_elem, "nvicPrioBits", "4"), 0) if cpu_elem is not None else 4

        device = Device(name=dev_name, version=dev_ver, description=dev_desc,
                        cpu_name=cpu_name, nvic_prio_bits=nvic_bits)

        periph_container = self.root.find("peripherals")
        if periph_container is None:
            return device

        # Крок 1: Базове зчитування модулів
        raw_peripherals = {}
        for p_node in periph_container.findall("peripheral"):
            p_obj = self._parse_peripheral_header(p_node)
            raw_peripherals[p_obj.name] = (p_node, p_obj)

        # Крок 2: Розв'язання успадкування derivedFrom
        for name, (p_node, p_obj) in raw_peripherals.items():
            if p_obj.derived_from:
                parent_name = p_obj.derived_from
                if parent_name in raw_peripherals:
                    parent_node, parent_obj = raw_peripherals[parent_name]
                    # Якщо батько ще не розпарсений — парсимо його регістри
                    if not parent_obj.registers:
                        self._parse_peripheral_registers(parent_node, parent_obj)
                    # Глибоке копіювання регістрів батька
                    p_obj.registers = [self._clone_register(r) for r in parent_obj.registers]
                    if not p_obj.header_struct_name:
                        p_obj.header_struct_name = parent_obj.header_struct_name or f"{parent_obj.name}_TypeDef"
                else:
                    print(f"УВАГА: Не знайдено батьківський модуль {parent_name} для {name}", file=sys.stderr)
            else:
                self._parse_peripheral_registers(p_node, p_obj)

            device.peripherals[p_obj.name] = p_obj

        return device

    def _get_text(self, parent: Optional[ET.Element], tag: str, default: str = "") -> str:
        if parent is None:
            return default
        elem = parent.find(tag)
        return elem.text.strip() if elem is not None and elem.text else default

    def _parse_peripheral_header(self, node: ET.Element) -> Peripheral:
        name = self._get_text(node, "name")
        base_addr = int(self._get_text(node, "baseAddress", "0"), 0)
        group = self._get_text(node, "groupName", name)
        struct_name = self._get_text(node, "headerStructName", "")
        desc = self._get_text(node, "description", "")
        derived = node.attrib.get("derivedFrom", None)

        p = Peripheral(name=name, base_address=base_addr, group_name=group,
                       header_struct_name=struct_name, description=desc, derived_from=derived)

        for int_node in node.findall("interrupt"):
            iname = self._get_text(int_node, "name")
            ival = int(self._get_text(int_node, "value", "0"), 0)
            idesc = self._get_text(int_node, "description", "")
            p.interrupts.append(Interrupt(name=iname, value=ival, description=idesc))

        return p

    def _parse_peripheral_registers(self, node: ET.Element, p: Peripheral):
        regs_node = node.find("registers")
        if regs_node is None:
            return

        for reg_node in regs_node.findall("register"):
            dim_text = self._get_text(reg_node, "dim", "")
            if dim_text:
                # Обробка масиву регістрів <dim>
                dim_count = int(dim_text, 0)
                dim_inc = int(self._get_text(reg_node, "dimIncrement", "4"), 0)
                dim_index = self._get_text(reg_node, "dimIndex", "")
                indices = self._parse_dim_indices(dim_count, dim_index)
                base_name = self._get_text(reg_node, "name")
                base_offset = int(self._get_text(reg_node, "addressOffset", "0"), 0)

                for idx_i, idx_val in enumerate(indices):
                    r_name = base_name.replace("%s", str(idx_val))
                    r_offset = base_offset + (idx_i * dim_inc)
                    reg_obj = self._parse_single_register(reg_node, r_name, r_offset)
                    p.registers.append(reg_obj)
            else:
                r_name = self._get_text(reg_node, "name")
                r_offset = int(self._get_text(reg_node, "addressOffset", "0"), 0)
                reg_obj = self._parse_single_register(reg_node, r_name, r_offset)
                p.registers.append(reg_obj)

    def _parse_dim_indices(self, count: int, index_str: str) -> List[str]:
        if not index_str:
            return [str(i) for i in range(count)]
        if "," in index_str:
            return [s.strip() for s in index_str.split(",")]
        if "-" in index_str:
            parts = index_str.split("-")
            start = int(parts[0], 0)
            end = int(parts[1], 0)
            return [str(i) for i in range(start, end + 1)]
        return [str(i) for i in range(count)]

    def _parse_single_register(self, node: ET.Element, name: str, offset: int) -> Register:
        size = int(self._get_text(node, "size", "32"), 0)
        access = self._get_text(node, "access", "read-write")
        reset_val = int(self._get_text(node, "resetValue", "0"), 0)
        reset_mask = int(self._get_text(node, "resetMask", "0xFFFFFFFF"), 0)
        desc = self._get_text(node, "description", "")
        mod_w = self._get_text(node, "modifiedWriteValues", "") or None
        read_a = self._get_text(node, "readAction", "") or None

        reg = Register(name=name, address_offset=offset, size=size, access=access,
                       reset_value=reset_val, reset_mask=reset_mask, description=desc,
                       modified_write=mod_w, read_action=read_a)

        fields_node = node.find("fields")
        if fields_node is not None:
            for f_node in fields_node.findall("field"):
                reg.fields.append(self._parse_field(f_node))

        return reg

    def _parse_field(self, node: ET.Element) -> BitField:
        name = self._get_text(node, "name")
        desc = self._get_text(node, "description", "")
        access = self._get_text(node, "access", "read-write")

        # Нормалізація формату меж бітового поля
        bit_offset = 0
        bit_width = 1

        if node.find("bitOffset") is not None:
            bit_offset = int(self._get_text(node, "bitOffset", "0"), 0)
            bit_width = int(self._get_text(node, "bitWidth", "1"), 0)
        elif node.find("lsb") is not None and node.find("msb") is not None:
            lsb = int(self._get_text(node, "lsb", "0"), 0)
            msb = int(self._get_text(node, "msb", "0"), 0)
            bit_offset = lsb
            bit_width = msb - lsb + 1
        elif node.find("bitRange") is not None:
            range_str = self._get_text(node, "bitRange", "[0:0]")
            m = re.match(r"\[(\d+):(\d+)\]", range_str)
            if m:
                msb = int(m.group(1))
                lsb = int(m.group(2))
                bit_offset = lsb
                bit_width = msb - lsb + 1

        f_obj = BitField(name=name, bit_offset=bit_offset, bit_width=bit_width,
                         access=access, description=desc)

        enum_node = node.find("enumeratedValues")
        if enum_node is not None:
            for ev_node in enum_node.findall("enumeratedValue"):
                ev_name = self._get_text(ev_node, "name")
                ev_val_str = self._get_text(ev_node, "value", "0")
                if ev_val_str.startswith("#"):
                    # Двійковий запис #0101
                    ev_val = int(ev_val_str[1:], 2)
                else:
                    ev_val = int(ev_val_str, 0)
                ev_desc = self._get_text(ev_node, "description", "")
                f_obj.enums.append(EnumValue(name=ev_name, value=ev_val, description=ev_desc))

        return f_obj

    def _clone_register(self, reg: Register) -> Register:
        return Register(
            name=reg.name, address_offset=reg.address_offset, size=reg.size,
            access=reg.access, reset_value=reg.reset_value, reset_mask=reg.reset_mask,
            description=reg.description, modified_write=reg.modified_write,
            read_action=reg.read_action,
            fields=[BitField(f.name, f.bit_offset, f.bit_width, f.access, f.description,
                             [EnumValue(e.name, e.value, e.description) for e in f.enums])
                    for f in reg.fields]
        )


class C99Generator:
    """Генератор системних заголовків мови C99 (стандарт CMSIS + _Static_assert)."""

    def __init__(self, device: Device):
        self.device = device

    def generate(self) -> str:
        out = []
        guard = f"__{self.device.name.upper()}_CMSIS_H__"
        out.append(f"#ifndef {guard}")
        out.append(f"#define {guard}\n")
        out.append("#include <stdint.h>")
        out.append("#include <stddef.h>\n")
        out.append("/* CMSIS Кваліфікатори доступу до апаратних регістрів */")
        out.append("#define __I     volatile const    /*!< Доступ лише для читання */")
        out.append("#define __O     volatile          /*!< Доступ лише для запису */")
        out.append("#define __IO    volatile          /*!< Доступ для читання й запису */\n")

        # 1. Таблиця векторів переривань IRQn_Type
        out.append("/* ============================================================================ */")
        out.append("/* ── Таблиця векторів переривань NVIC ──────────────────────────────────────── */")
        out.append("/* ============================================================================ */")
        out.append("typedef enum {")
        out.append("    /* Системні винятки процесорного ядра ARM Cortex-M */")
        out.append("    NonMaskableInt_IRQn   = -14,")
        out.append("    HardFault_IRQn        = -13,")
        out.append("    MemoryManagement_IRQn = -12,")
        out.append("    BusFault_IRQn         = -11,")
        out.append("    UsageFault_IRQn       = -10,")
        out.append("    SVCall_IRQn           = -5,")
        out.append("    PendSV_IRQn           = -2,")
        out.append("    SysTick_IRQn          = -1,")
        out.append("    /* Периферійні переривання мікроконтролера */")

        interrupts_seen = set()
        for p in self.device.peripherals.values():
            for intr in p.interrupts:
                if intr.value not in interrupts_seen:
                    interrupts_seen.add(intr.value)
                    desc_comment = f" /*!< {intr.description} */" if intr.description else ""
                    out.append(f"    {intr.name}_IRQn = {intr.value},{desc_comment}")
        out.append(f"}} IRQn_Type;\n")

        # 2. Унікальні структури периферійних модулів
        out.append("/* ============================================================================ */")
        out.append("/* ── Структури периферійних модулів із вирівнюванням пам'яті ────────────────── */")
        out.append("/* ============================================================================ */")

        generated_structs = set()
        for p in self.device.peripherals.values():
            struct_name = p.header_struct_name or f"{p.name}_TypeDef"
            if struct_name in generated_structs or not p.registers:
                continue
            generated_structs.add(struct_name)

            out.append(self._generate_struct(struct_name, p.registers))
            out.append("")

        # 3. Бітові маски та позиції для кожного регістра
        out.append("/* ============================================================================ */")
        out.append("/* ── Бітові маски, зсуви та константи переліків ────────────────────────────── */")
        out.append("/* ============================================================================ */")
        for p in self.device.peripherals.values():
            for reg in p.registers:
                prefix = f"{p.group_name or p.name}_{reg.name}"
                for f in reg.fields:
                    f_name = f"{prefix}_{f.name}"
                    out.append(f"#define {f_name}_Pos ({f.bit_offset}U)")
                    out.append(f"#define {f_name}_Msk (0x{((1 << f.bit_width) - 1):X}U << {f_name}_Pos)")
                    out.append(f"#define {f_name}     {f_name}_Msk")

                    for ev in f.enums:
                        ev_name = f"{f_name}_{ev.name.upper()}"
                        out.append(f"#define {ev_name} (0x{ev.value:X}U << {f_name}_Pos)")
                if reg.fields:
                    out.append("")

        # 4. Базові адреси та екземпляри периферії
        out.append("/* ============================================================================ */")
        out.append("/* ── Базові адреси та екземпляри периферійних блоків ───────────────────────── */")
        out.append("/* ============================================================================ */")
        for p in self.device.peripherals.values():
            base_macro = f"{p.name}_BASE"
            out.append(f"#define {base_macro} (0x{p.base_address:08X}UL)")
            struct_name = p.header_struct_name or f"{p.name}_TypeDef"
            out.append(f"#define {p.name} (( {struct_name} * ) {base_macro})")

        out.append(f"\n#endif /* {guard} */")
        return "\n".join(out)

    def _generate_struct(self, struct_name: str, registers: List[Register]) -> str:
        lines = [f"typedef struct {{"]
        sorted_regs = sorted(registers, key=lambda r: r.address_offset)

        cur_offset = 0
        res_idx = 0
        assert_lines = []

        for reg in sorted_regs:
            # Перевірка на прогалину в пам'яті (Address Gap)
            if reg.address_offset > cur_offset:
                gap = reg.address_offset - cur_offset
                lines.append(f"    uint8_t  RESERVED_{res_idx}[{gap}]; /*!< Зсув 0x{cur_offset:04X}..0x{reg.address_offset-1:04X} */")
                res_idx += 1
                cur_offset = reg.address_offset

            qual = "__IO"
            if reg.access == "read-only":
                qual = "__I "
            elif reg.access == "write-only":
                qual = "__O "

            type_name = "uint32_t"
            type_size = 4
            if reg.size == 8:
                type_name = "uint8_t "
                type_size = 1
            elif reg.size == 16:
                type_name = "uint16_t"
                type_size = 2
            elif reg.size == 64:
                type_name = "uint64_t"
                type_size = 8

            lines.append(f"    {qual} {type_name} {reg.name}; /*!< Зсув 0x{reg.address_offset:04X}: {reg.description} */")
            assert_lines.append(f"_Static_assert(offsetof({struct_name}, {reg.name}) == 0x{reg.address_offset:X}, \"Помилка зміщення {struct_name}->{reg.name}\");")
            cur_offset += type_size

        lines.append(f"}} {struct_name};\n")
        lines.append("/* Валідація мапи пам'яті компілятором під час збирання */")
        lines.extend(assert_lines)
        return "\n".join(lines)


class Cpp20Generator:
    """Генератор сучасних C++20 типобезпечних заголовків (concepts, enum class, constexpr)."""

    def __init__(self, device: Device):
        self.device = device

    def generate(self) -> str:
        out = []
        guard = f"__{self.device.name.upper()}_HAL_REGS_HPP__"
        out.append(f"#ifndef {guard}")
        out.append(f"#define {guard}\n")
        out.append("#include <cstdint>")
        out.append("#include <cstddef>")
        out.append("#include <concepts>\n")
        out.append(f"namespace {self.device.name.lower()}::hal {{\n")

        # 1. Політики та концепти доступу
        out.append("// ── Політики та концепти апаратного доступу ─────────────────────────")
        out.append("struct ReadOnlyPolicy {};")
        out.append("struct WriteOnlyPolicy {};")
        out.append("struct ReadWritePolicy {};\n")

        out.append("template <typename T>")
        out.append("concept Readable = std::same_as<T, ReadOnlyPolicy> || std::same_as<T, ReadWritePolicy>;\n")

        out.append("template <typename T>")
        out.append("concept Writable = std::same_as<T, WriteOnlyPolicy> || std::same_as<T, ReadWritePolicy>;\n")

        # 2. Шаблонне бітове поле
        out.append("// ── Типобезпечне бітове поле з кодуванням значень ─────────────────────")
        out.append("template <uint32_t Offset, uint32_t Width, typename ValueType = uint32_t>")
        out.append("struct BitField {")
        out.append("    static constexpr uint32_t pos = Offset;")
        out.append("    static constexpr uint32_t width = Width;")
        out.append("    static constexpr uint32_t mask = ((1UL << Width) - 1UL) << pos;\n")
        out.append("    [[nodiscard]] static constexpr uint32_t encode(ValueType val) noexcept {")
        out.append("        return (static_cast<uint32_t>(val) << pos) & mask;")
        out.append("    }\n")
        out.append("    [[nodiscard]] static constexpr ValueType decode(uint32_t reg_val) noexcept {")
        out.append("        return static_cast<ValueType>((reg_val & mask) >> pos);")
        out.append("    }")
        out.append("};\n")

        # 3. Шаблон регістра
        out.append("// ── Типобезпечний апаратний регістр із нульовими накладними витратами ──")
        out.append("template <uintptr_t Address, typename AccessPolicy = ReadWritePolicy, typename RegType = uint32_t>")
        out.append("class Register {")
        out.append("public:")
        out.append("    static constexpr uintptr_t address = Address;\n")
        out.append("    [[nodiscard]] static inline RegType read() noexcept requires Readable<AccessPolicy> {")
        out.append("        return *reinterpret_cast<volatile RegType*>(address);")
        out.append("    }\n")
        out.append("    static inline void write(RegType val) noexcept requires Writable<AccessPolicy> {")
        out.append("        *reinterpret_cast<volatile RegType*>(address) = val;")
        out.append("    }\n")
        out.append("    template <typename Field, typename ValType>")
        out.append("    static inline void set_field(ValType val) noexcept requires Readable<AccessPolicy> && Writable<AccessPolicy> {")
        out.append("        RegType current = read();")
        out.append("        current &= ~Field::mask;")
        out.append("        current |= Field::encode(val);")
        out.append("        write(current);")
        out.append("    }")
        out.append("};\n")

        # 4. Моделювання модулів та полів
        for p in self.device.peripherals.values():
            out.append(f"namespace {p.name.lower()} {{")
            out.append(f"    inline constexpr uintptr_t base_addr = 0x{p.base_address:08X}UL;\n")

            for reg in p.registers:
                reg_addr_expr = f"base_addr + 0x{reg.address_offset:04X}UL"
                pol = "ReadWritePolicy"
                if reg.access == "read-only":
                    pol = "ReadOnlyPolicy"
                elif reg.access == "write-only":
                    pol = "WriteOnlyPolicy"

                out.append(f"    // Регістр {reg.name} (Зсув 0x{reg.address_offset:04X}): {reg.description}")
                out.append(f"    using {reg.name} = Register<{reg_addr_expr}, {pol}, uint32_t>;\n")

                if reg.fields:
                    out.append(f"    struct {reg.name}_Fields {{")
                    for f in reg.fields:
                        val_type = "uint32_t"
                        if f.enums:
                            enum_name = f"{f.name}_Enum"
                            out.append(f"        enum class {enum_name} : uint32_t {{")
                            for ev in f.enums:
                                out.append(f"            {ev.name} = 0x{ev.value:X},")
                            out.append(f"        }};")
                            val_type = enum_name
                        elif f.bit_width == 1:
                            val_type = "bool"

                        out.append(f"        using {f.name} = BitField<{f.bit_offset}, {f.bit_width}, {val_type}>;")
                    out.append(f"    }};\n")

            out.append(f"}} // namespace {p.name.lower()}\n")

        out.append(f"}} // namespace {self.device.name.lower()}::hal\n")
        out.append(f"#endif /* {guard} */")
        return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        print("Використання: python svd_generator.py <input.svd> [c99_out.h] [cpp20_out.hpp]")
        sys.exit(1)

    svd_file = sys.argv[1]
    c99_file = sys.argv[2] if len(sys.argv) > 2 else "device_c99.h"
    cpp_file = sys.argv[3] if len(sys.argv) > 3 else "device_cpp20.hpp"

    print(f"Парсинг SVD файлу: {svd_file}...")
    parser = SvdParser(svd_file)
    device = parser.parse()

    print(f"Пристрій: {device.name} (Ядро: {device.cpu_name}, Периферія: {len(device.peripherals)} модулів)")

    print(f"Генерація C99 заголовка в {c99_file}...")
    c99_gen = C99Generator(device)
    with open(c99_file, "w", encoding="utf-8") as f:
        f.write(c99_gen.generate())

    print(f"Генерація C++20 заголовка в {cpp_file}...")
    cpp_gen = Cpp20Generator(device)
    with open(cpp_file, "w", encoding="utf-8") as f:
        f.write(cpp_gen.generate())

    print("Генерацію успішно завершено!")


if __name__ == "__main__":
    main()
