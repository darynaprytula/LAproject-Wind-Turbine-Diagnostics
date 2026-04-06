# LAprojectWindTurbineDiagnostics

Condition monitoring of rotating machines using vibration signals.  
Wind turbine defect diagnostics based on vibration analysis.

---

## Project Overview

The goal of this project is to detect mechanical faults in operating machines using vibration signal analysis, with a focus on wind turbines.  
The approach combines signal processing and statistical methods to identify early signs of defects in mechanical components such as bearings, gears, and shafts.

Wind turbines operate continuously, often in remote locations, so early fault detection is essential to prevent failures, reduce maintenance costs, and improve reliability.

---

## Dataset

We use real vibration data collected from wind turbines:

- 4 turbines: WTG511, WTG513, WTG515, WTG656  
- 8 accelerometers (sensors)  
- 2815 signal records  
- Duration per signal: 6 hours  
- Frequency band: 1000 Hz  
- Frequency resolution: ~0.156 Hz  

Each signal contains both vibration data and metadata (timestamp, operating conditions, sensor ID, etc.), which are used for further analysis.

---

## Methodology

Our pipeline consists of five main stages:

1. Signal representation  
2. Time-domain analysis  
3. Frequency-domain analysis (FFT)  
4. Frequency-selective feature extraction  
5. Trend analysis  

---

## Algorithm Description

### Time-domain analysis
We compute statistical features such as:
- mean  
- RMS  
- standard deviation  
- kurtosis  
- crest factor  
- impulse factor  

These describe the overall behavior of the vibration signal.

---

### Frequency-domain analysis (FFT)

We transform the signal into the frequency domain using the Fast Fourier Transform (FFT) to identify dominant frequencies.

We implemented two versions of FFT:
- **Manual recursive FFT** (Cooley–Tukey algorithm)  
- **NumPy FFT** (used for validation)

Before applying FFT:
- the signal is zero-padded to the next power of two  
- this improves computational efficiency and frequency resolution  

We construct a **one-sided amplitude spectrum**:
- frequencies from 0 to Nyquist frequency \( f_s / 2 \)  
- normalization by signal length  
- amplitudes doubled (except DC and Nyquist components)  

---

### Frequency-selective features

We extract amplitudes at characteristic frequencies of mechanical components:

- bearings (BPFO, BPFI, FTF, BSF)  
- gears (gear mesh frequencies and harmonics)  

Key steps:
- compute expected frequencies using rotation speed  
- consider only frequencies below Nyquist limit  
- search for peak amplitude within ±1 Hz band  

This makes the method robust to:
- spectral leakage  
- frequency discretization  
- small variations in rotation speed  

---

### Trend analysis

We analyze how features evolve over time using the **Mann–Kendall test**.

- detects monotonic trends  
- used for early fault detection  
- threshold: \( Z \geq 3.5 \) → potential defect  

---

## Key Features

- Manual implementation of FFT (radix-2 Cooley–Tukey)  
- Validation against NumPy FFT  
- Physically interpretable features  
- No labeled data required  
- Robust frequency-based diagnostics  

---

## Pros and Cons

### Pros
- Interpretable results linked to physical components  
- Works without labeled data  
- Computationally efficient  
- Suitable for real industrial monitoring  

### Cons
- Requires known mechanical parameters  
- Sensitive to rotation speed estimation  
- Fixed ±1 Hz band may require tuning  

---

## Implementation Pipeline

Completed steps:

- Load vibration signal data  
- Structure data  
- Define sampling frequency  
- Convert signal to vector \( x[n] \)  
- Compute time-domain features  
- Compute FFT (manual + NumPy)  
- Validate FFT results  
- Compute amplitude spectrum  
- Extract frequency-selective features  
- Perform trend analysis  
- Apply Mann–Kendall test  
- Detect potential defects  
- Visualize spectra and features  

Planned:

- Test the pipeline on signals with different frequency bands  
  (currently all signals have 1000 Hz frequency span)  

---

## Technologies Used

- Python  
- NumPy  
- Matplotlib  

---

## Team Video Presentations

Each team member prepared an individual video presentation:

- Daryna Prytula – [Watch video](https://your-link-1)
- Sofiia Pereima – [Watch video](https://youtu.be/V23egEHX_H0)
- Bohdana Zubrytska – [Watch video](https://your-link-3)

