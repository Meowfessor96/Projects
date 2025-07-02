# Solar Wireless Mobile Charger 🔋☀️

A compact and sustainable solution for wireless mobile charging using solar energy, inductive coupling, and efficient power management. This project enables on-the-go, eco-friendly mobile device charging without relying on grid power.

---

## 📌 Abstract

This project presents the development of a solar-powered wireless mobile charger. It uses photovoltaic cells to charge a battery, which then powers a wireless charging coil. Compatible devices can be charged wirelessly through inductive coupling, offering convenience and environmental benefits.

---

## 🧠 Theory

- **Electromagnetic Induction**
- **Inductive Coupling**
- **Wireless Power Transfer using Coils**

---

## 🛠️ Components Used

| Component | Quantity |
|----------|----------|
| Copper Wire (25 gauge) | 2 |
| IRFZ44N MOSFET | 1 |
| Solar Panel (12V) | 1 |
| IC4007 Diodes | 5 |
| LM7805 | 1 |
| KA7809 | 1 |
| Capacitors, Resistors | Various |
| Rechargeable Cells (ICR18650) | 2 |
| Breadboard | 3 |

(See [components.md](components.md) for full specs.)
ww

---

## 🔧 Circuit Design

- ✅ **Transmitter Circuit** — converts DC to AC and generates magnetic field
- ✅ **Receiver Circuit** — rectifies AC to DC and regulates to 5V
- ✅ **Power Bank Circuit** — charges batteries for cloudy use

(See schematic images in the [images/](images/) folder.)


---

## 📊 Observations

| Distance (mm) | Output Voltage (V) |
|---------------|--------------------|
| 0             | 4.97               |
| 10            | 4.29               |
| 20            | 3.00               |

> Wireless efficiency decreases with distance. Optimal below 10mm.

---

## ✅ Conclusion

The charger successfully converts solar energy to wireless power with regulated 5V DC output, suitable for mobile devices. This validates the reliability of wireless solar-powered systems for portable use.

---

## 📁 Files & Structure


