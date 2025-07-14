# 5-bit SAR ADC using Arduino, BCD Encoder, and LEDs

This project demonstrates a **hardware-based 5-bit SAR (Successive Approximation Register) ADC** using an **Arduino**, a **BCD encoder**, and **LEDs** to display the digital output. It mimics how microcontrollers perform analog-to-digital conversion, but using **pure hardware logic**.

---

## 🧠 Project Overview

A SAR ADC works by comparing an analog input voltage against a series of reference voltages, one bit at a time, starting from the **Most Significant Bit (MSB)**. For each step, the result of the comparison decides whether the bit is set to `1` or `0`.

In this project:

- The analog input is compared using a **custom DAC** and a comparator setup.
- A **BCD encoder** simplifies and encodes the logic.
- The **final 5-bit digital output** is shown using **5 LEDs**:
  - 🔴 LED ON → Bit = `1`
  - ⚫ LED OFF → Bit = `0`

---

## ⚙️ Hardware Components Used

- 🟦 **Arduino Uno** – generates voltage references or controls the DAC logic
- 🧮 **BCD Encoder IC** – converts comparator decisions into 5-bit binary output
- 🧪 **Comparator circuit** – compares analog input to DAC output
- 🔌 **Resistor ladder / voltage divider** – for generating analog voltages
- 🔘 **5 LEDs** – show binary output (from MSB to LSB)
- ⛓️ **Breadboard & jumper wires** – for prototyping
- 🟫 **Resistors** – for current-limiting and DAC precision

> ⚠️ No internal software ADC is used — all logic is **hardware-driven**.

---

## 🔢 LED Output and Voltage Mapping

Each 5-bit binary output represents a **digital level from 0 to 31** (`2⁵ - 1 = 31`).  
If **2.0V** is considered the maximum input voltage, then:

### ➕ 1 Digital Step = 2.0V / 31 ≈ **0.0645V (64.5mV)**

So, each binary output maps to a voltage level approximately as:

Digital Output: N
Voltage ≈ (N / 31) × 2.0V


---

### 📺 Sample Readings from Demo:

| Input Voltage | Binary Output | Decimal Value | LED Display (MSB → LSB) | Approx Voltage from Code | Error (V) |
|---------------|---------------|---------------|---------------------------|---------------------------|-----------|
| 2.0V          | `11111`       | 31            | 🔴 🔴 🔴 🔴 🔴             | (31/31) × 2.0V = 2.0V     | ±0.0V     |
| 1.6V          | `11000`       | 24            | 🔴 🔴 ⚫ ⚫ ⚫             | (24/31) × 2.0V ≈ 1.55V    | ~ -0.05V  |
| 1.4V          | `10110`       | 22            | 🔴 ⚫ 🔴 🔴 ⚫             | (22/31) × 2.0V ≈ 1.42V    | ~ +0.02V  |
| 1.2V          | `10011`       | 19            | 🔴 ⚫ ⚫ 🔴 🔴             | (19/31) × 2.0V ≈ 1.23V    | ~ +0.03V  |

> 🧮 Small errors (~±0.05V) may appear due to resistor tolerances, comparator offsets, or DAC resolution.

---

## 🧰 How It Works

1. **Analog Input** is connected to a comparator system.
2. **Arduino or DAC logic** generates reference voltages for comparison.
3. **Comparator outputs** are fed into a **BCD encoder**, which translates them into a binary value.
4. **5 LEDs** show the binary result visually.
5. Final result gives an idea of where the input voltage stands between 0V and 2V.

---

## 🧭 Interpreting Output

- LED pattern represents a 5-bit binary number.
- Binary `11111` = Decimal `31` → Maximum voltage (2.0V)
- Binary `00000` = Decimal `0` → Minimum voltage (0V)
- Every step ≈ **64.5mV**
- So, a binary value of `N` means:  
  ➡️ **Approx Voltage = (N × 64.5mV)**

---

## 🧪 Applications & Learnings

- Demonstrates how SAR ADCs work at a hardware level
- Reinforces core electronics concepts:
  - DACs and comparators
  - Binary encoding using BCD
  - Digital output interpretation using LEDs
- Great for beginner-level ADC understanding and hardware debugging

---
