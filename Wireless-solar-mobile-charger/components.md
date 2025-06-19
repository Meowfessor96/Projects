# 📦 Components Used – Solar Wireless Mobile Charger

This document lists and explains the components used in the Solar Wireless Mobile Charger project.

---

## 🔧 1. Copper Wire (25 Gauge)

- **Quantity**: 2 coils (30 turns each)
- **Use**: Forms the transmitter and receiver coils for inductive coupling
- **Spec**: 25 AWG enameled copper wire
- **Function**: Carries AC current to create a magnetic field

---

## ⚡ 2. IRFZ44N MOSFET

- **Type**: N-Channel Enhancement MOSFET
- **Drain Current**: Up to 49A
- **Rds(on)**: 17.5 mΩ
- **Vgs(th)**: 2V
- **Use**: Acts as a switch in the inverter circuit of the transmitter
- **Reason**: High current capability and fast switching

---

## ☀️ 3. Solar Panel (12V)

- **Output Voltage**: 12V (under optimal sunlight)
- **Use**: Main power source for charging the battery
- **Reason**: Enables portable and eco-friendly energy harvesting

---

## 🔋 4. ICR18650 Rechargeable Cells

- **Quantity**: 2
- **Type**: Lithium-Ion
- **Use**: Stores energy from the solar panel
- **Reason**: High energy density and reusability

---

## 🔌 5. Voltage Regulators (LM7805 & KA7809)

- **LM7805**:
  - Output: +5V DC
  - Use: Powers the receiver output to charge mobile devices
- **KA7809**:
  - Output: +9V DC
  - Use: For battery charging
- **Reason**: Provide regulated voltage for safe device operation

---

## 🔁 6. Diodes (IC4007)

- **Type**: Rectifier Diodes
- **Quantity**: 5
- **Use**: Build a full-bridge rectifier in the receiver
- **Reason**: Converts AC (from induction) to DC

---

## 🔘 7. Capacitors

| Type        | Quantity | Use                                   |
|-------------|----------|----------------------------------------
| 1000 µF     | 1        | Filtering high ripple DC              |
| 100 µF      | 1        | Filtering secondary circuits           |
| 4.7 nF      | 1        | LC tank circuit for oscillation        |
| 1 nF        | 2        | Gate filtering                         |
| 220 nF      | 1        | Tap point stabilization                |

---

## 🧮 8. Resistors

| Resistance | Quantity | Use                                |
|------------|----------|-------------------------------------|
| 1 kΩ       | 3        | Load handling, tap filtering       |
| 100 Ω      | 2        | Gate protection, current limiting  |
| 5 kΩ       | 1        | Input filtering                    |

---

## 🔅 9. Breadboards

- **Quantity**: 3
- **Use**: Circuit prototyping
- **Reason**: Easy assembly without soldering

---

## 📁 Sources / Datasheets

- [IRFZ44N Datasheet](https://www.vishay.com/docs/91328/91328.pdf)
- [LM7805 Datasheet](https://www.ti.com/lit/ds/symlink/lm7805.pdf)
- [ICR18650 Info](https://www.nkon.nl/sk/k/keeppower-18650-3120mah.html)

---

> 📌 All components were selected for their compatibility with low-cost, student-accessible prototyping and renewable energy use-cases.

