# 🎧 Adaptive Noise Cancellation using NLMS and Notch Filtering

This repository contains a MATLAB implementation of **adaptive noise suppression** using the **Normalized Least Mean Squares (NLMS)** algorithm. The system optionally applies **IIR Notch Filtering** for tonal noise cancellation. This is part of a project aimed at enhancing speech signals corrupted by external environmental noise.

> 📄 The full project explanation and design choices are available in [`TEAM11.pdf`](TEAM11.pdf)

---

## 📂 Repository Contents

| File          | Description                                           |
|---------------|-------------------------------------------------------|
| `main.m`      | MATLAB code implementing NLMS-based noise filtering   |
| `graph.png`   | Graphical result (e.g., SNR plot or waveform overlay) |
| `TEAM11.pdf`  | Project documentation and theoretical explanation     |

---

## 🎯 Objective

Remove background noise from a noisy speech signal using:
- **FIR Adaptive Filtering** with coefficient updates via **NLMS**
- Optional **Notch Filtering** to suppress specific tonal frequencies (e.g., electrical hum)

The goal is to improve the **Signal-to-Noise Ratio (SNR)** and reconstruct clean speech from corrupted input.

---

## 🧠 How It Works

### 🟦 1. Inputs (Expected but not bundled here)
- External noise vector `w(n)`
- Noisy speech `s(n) + v(n)`
- Clean speech `s(n)` (for evaluation only)

> You can load your own `*.txt` files in the same format. The system assumes sampling rate `Fs = 44100 Hz`.

### 🟩 2. Processing
- If `tonal_freqs` is empty → **Full suppression using NLMS**
- If `tonal_freqs` contains frequency values → **Partial suppression** using notch filters + NLMS
- Error signal `e(n)` is computed as:
e(n) = s(n) + v(n) - hᵀw(n)
and the coefficients `h` are updated adaptively.

- The enhanced output is written to a WAV file and compared against the clean signal for **SNR improvement**.

### 🟥 3. Optional IIR Notch Filter
- Designed to remove tonal components like 1kHz or 3kHz hum
- Notch bandwidth: `10 Hz`
- Can be toggled via the `tonal_freqs` variable

---

## 🧪 Example Code Snippet

```matlab
mu = 0.007;
filter_order = 2;
tonal_freqs = [];  % e.g., [1000, 3000] for partial suppression

% Main adaptive filtering loop
for i = 1:N
  % Optional notch
  ...
  % NLMS adaptation
  y = h' * buffer;
  e = noisy_speech(i) - y;
  h = h + mu * e * buffer / (epsilon + buffer' * buffer);
  output(i) = e;
end


