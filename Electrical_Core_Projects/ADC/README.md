# 5-bit SAR ADC using Arduino, BCD Encoder, and LEDs

This project demonstrates a hardware-based 5-bit Successive Approximation Register (SAR) ADC implemented on a breadboard. It uses an Arduino for voltage reference/control, a custom DAC for comparison, and a **BCD encoder** to simplify the binary output logic. The resulting 5-bit digital output is visualized using 5 LEDs.

---

## 🧠 Project Overview

A SAR ADC converts an analog voltage to digital by performing bit-by-bit approximation — starting from the Most Significant Bit (MSB) and narrowing down using comparator feedback. Each comparison step sets a bit in the digital output.

In this setup:

- An **analog input voltage** is compared with DAC-generated values.
- A **BCD encoder** processes logic decisions and helps output valid binary sequences.
- The final 5-bit result is displayed on **LEDs**, with:
  - LED ON = bit `1`
  - LED OFF = bit `0`

---

## ⚙️ Hardware Components Used

- 🟦 **Arduino Uno** – provides voltage reference or control for the DAC
- 🧮 **BCD Encoder IC** – encodes comparator outputs to binary representation
- ⚡ **Resistor Ladder / Voltage Divider** – generates analog test voltages
- 🔘 **5 LEDs** – represent the 5-bit binary output (MSB to LSB)
- ⚙️ **Discrete logic components and DAC circuit**
- ⛓️ **Breadboard + Jumper wires** – for hardware prototyping
- 🟫 **Resistors** – for voltage division and current-limiting on LEDs

> 🔎 The conversion logic is purely hardware-driven — no software-based ADC is used.

---

## 🔢 LED Output and Voltage Mapping

Below are the observed outputs from the demo video:

| Input Voltage | 5-bit Binary Output | LED Display (MSB → LSB) |
|---------------|---------------------|--------------------------|
| 2.0V          | `11111`             | 🔴 🔴 🔴 🔴 🔴            |
| 1.6V          | `11000`             | 🔴 🔴 ⚫ ⚫ ⚫            |
| 1.4V          | `10110`             | 🔴 ⚫ 🔴 🔴 ⚫            |
| 1.2V          | `10011`             | 🔴 ⚫ ⚫ 🔴 🔴            |

(🔴 = LED ON, ⚫ = LED OFF)

---

## 🧰 How It Works

1. The analog input is connected to a comparator system driven by a DAC.
2. The Arduino likely controls DAC steps or feeds in voltage references.
3. At each bit decision, the comparator result is sent to a **BCD encoder**.
4. The encoder outputs binary values representing the voltage level.
5. LEDs display the resulting 5-bit binary code.

---

## 🎯 Output Interpretation

- Each LED corresponds to a bit: **[Bit4, Bit3, Bit2, Bit1, Bit0]**
- As voltage increases, higher bits turn ON.
- Maximum voltage (~2.0V) results in all LEDs ON (`11111`).
- Lower voltages result in sparser LED patterns (e.g., `10011`).

---

## 🧪 Applications & Learnings

- Demonstrates hardware-level analog-to-digital conversion
- Reinforces concepts of DACs, comparators, encoders, and digital output interpretation
- Good educational example of SAR ADC principles without needing microcontroller computation

---

## 📁 Recommended Repo Structure

