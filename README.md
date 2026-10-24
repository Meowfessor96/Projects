# Project Portfolio

A collection of coursework and personal projects in predictive modelling, machine learning, software development, and electrical engineering. Each link opens the project's code, documentation, or hardware demonstrations.

## Predictive Modelling, Machine Learning, and Software

### [Predicting Footballer Market Values](./football-market-value-prediction/)

FIFA 23 market-value modelling in R / RStudio using PCA, K-means clustering, and pooled versus role-specific regression. Reduced 29 skill variables to four components retaining 78.1% of variance and evaluated regression models using a 13,396-player hold-out set. Includes the R analysis script, the project presentation, and setup documentation. The code distinguishes the role-specific model without potential (reported hold-out R-squared 0.942) from the model with potential (0.965), evaluated on log market value.

### [Counter-Strike Match Outcome Predictor](./cs-predictor/)

A Python notebook for predicting professional CS:GO match outcomes using logistic regression, time-decayed team features, economy-state Markov models, dynamic programming, and Monte Carlo simulation. The recorded evaluation reaches 61.9% accuracy on 299 held-out matches against a 57.5% rank-only baseline. The current data uses CS:GO MR15 rules; adapting the configuration for CS2 does not constitute validation on modern CS2 matches.

### [GitHub Repo Intelligence](./git-repo-assistance/)

A Chrome extension with a JavaScript sidebar and local Flask backend. Combines GitHub REST API metadata with Groq-hosted Llama 3.3 to generate structured repository summaries, inferred technology and architecture information, suggested entry points, and related-repository recommendations.

### [Valorant Object Detection](./valorant-classifier/)

A YOLOv8s object detector for enemies, teammates, dropped spikes, and planted spikes in Valorant gameplay frames. The saved notebook evaluation reports 0.995 mAP@50 and 0.767 mAP@50-95 on 988 test images, with 11.4 ms inference per image on an RTX 3050 laptop GPU.

### [Binary Classification and Statistical Learning](./Binary-Classification-Using-Logistic-Regression/)

Python / NumPy implementations of least-squares classification, linear and Fisher discriminant projections, perceptron, logistic regression, Gaussian decision boundaries, and Gaussian mixture estimation with expectation-maximization. Includes synthetic-data experiments and decision-boundary visualizations.

### [KNN Image Classifier](./KNN-Classifier/)

A nearest-neighbour classification notebook with a custom NumPy implementation for synthetic data, repeated hold-out selection of k, and a scikit-learn MNIST experiment comparing neighbour counts and distance metrics. Includes decision-region and confusion-matrix plotting code; saved outputs should be checked before claiming a completed MNIST test score.

## Electrical Engineering

### [5-bit SAR ADC with R-2R DAC](./Electrical_Core_Projects/ADC/)

Hardware successive-approximation ADC using D flip-flop control logic, an R-2R ladder DAC, and an LM358 comparator circuit. Arduino supplies clock and enable signals. Includes the lab report and a hardware demonstration.

### [FM Transmitter](./Electrical_Core_Projects/FM-transmitter/)

A 9 V BC547 transistor-based FM transmitter with microphone input, an LC resonant circuit, and a wire antenna. Includes a handwritten circuit report and a theoretical carrier-frequency calculation.

### [Audio Amplifier](./Electrical_Core_Projects/Audio-amplifier/)

An LM386 microphone-to-speaker amplifier with volume control, capacitive coupling, bypassing, and gain configuration. Includes circuit documentation and frequency-response / noise analysis.

### [Seven-Segment Digital Clock](./Electrical_Core_Projects/7-segment-digital-clock/)

A breadboard digital clock using logic ICs and seven-segment displays. Hardware videos demonstrate the hours/minutes and seconds displays.

### [Adaptive Digital Noise Filter](./Electrical_Core_Projects/Digital-noise-filter/)

MATLAB implementation of NLMS adaptive FIR noise cancellation with an optional IIR notch-filter cascade in the reference-noise path. Supports full suppression and partial suppression modes, SNR evaluation, and enhanced-audio export.

### [Solar Wireless Mobile Charger](./Electrical_Core_Projects/Wireless-solar-mobile-charger/)

A solar-powered inductive charging prototype with battery backup, a MOSFET transmitter, bridge rectification, filtering, and voltage regulation. Includes schematics, component notes, hardware observations, and measured output voltage versus coil separation.

## Navigation and Scope

The list above contains the 12 project folders currently present in this repository. Reports and saved notebook outputs describe the work performed; some folders do not include the original datasets, source code, or full reproduction environment.
