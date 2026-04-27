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

This repository includes only the 1K frequency signal files, which are sufficient for testing the project. The complete dataset is available via the link below because it is too large to store directly in GitHub.

[All signals](https://drive.google.com/drive/folders/1lNUXeU5XNpskOdd4gJ6OJgpvY8bOLp0S?usp=sharing)

After downloading, place the contents into the signals-by-sensors/ folder in the project root,
keeping the folder structure: signals-by-sensors/data-WTG511/1/, data-WTG511/2/, ..., data-WTG656/8/

We use real vibration data collected from wind turbines:

- 4 turbines: WTG511, WTG513, WTG515, WTG656  
- 8 accelerometers (sensors)  
- 4706 signal records    
- Duration per signal: 6 hours  
- Frequency band: 1000 Hz and 10000 Hz
- Frequency resolution: ~0.156 Hz  

Each signal contains both vibration data and metadata (timestamp, operating conditions, sensor ID, etc.), which are used for further analysis.

Note on timestamp: all timestamps in the dataset have a +10 year offset applied  by the data provider. A value corresponding to January 2016 in Unix time represents January 2026 in this dataset. 

---

## Methodology

The pipeline consists of five main stages:

1. Signal representation - parsing metadata from filenames, load signals from JSON files
2. Time-domain analysis - computing statistical features (RMS, Kurtosis, Crest Factor, etc.)
3. Frequency-domain analysis (FFT and amplitude spectrum construction)  
4. Frequency-selective feature extraction - amplitudes at characteristic fault frequencies
5. Trend analysis - Mann–Kendall test for early degradation detection

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

## Pros and Cons of our algorithms

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

## Project Structure

The repository is organized into modular components, each responsible for a specific stage of the pipeline.

---

### signals-by-sensors/

Raw dataset organized by turbines and sensors.

  - `data-WTG511/`, `data-WTG513/`, `data-WTG515/`, `data-WTG656/` – signal files for each turbine containing signals collected from 8 sensors

---

### config/

Contains configuration files and physical parameters used in the analysis.

  - `Kinematics.json` – mechanical characteristics of components (e.g., bearing frequencies such as BPFO, BPFI, etc.)
  - `parameters.py` – global constants, thresholds, and processing settings

---

### utils/

Utility functions used across the project.

 - `helpers.py` – helper functions (e.g., string cleaning for safe filenames)

---

### data/

Responsible for loading and organizing raw vibration data.

  - `signal_loader.py` – loads vibration signals and metadata from files
  - `sorting_signals.py` – groups and structures signals (by turbine, sensor, etc.)

---

### features/

Implements feature extraction from vibration signals in both time and frequency domains.

  - `fft.py` – manual FFT implementation (Cooley–Tukey) and comparison with NumPy
  - `amplitude_spectrum.py` – computation of one-sided amplitude spectrum
  - `broadband_characteristics.py` – broadband vibration features
  - `operating_stats.py` – time-domain statistical features (RMS, kurtosis, etc.)
  - `fsc.py` – frequency-selective characteristics extraction
  - `plot_spectra.py` – visualization of spectra
  - `compare_plots.py` – comparison plots (manual FFT vs NumPy FFT)

---

### trend_analysis/

Implements trend detection and fault diagnostics.

  - `trend_analysis.py` – main logic for trend computation
  - `metrics_trend.py` – tracking feature evolution over time
  - fsc_trend.py` – trends of frequency-selective features
  - `classification.py` – classification of potential defects
  - `thresholds.py` – threshold definitions for anomaly detection
  - `trend_plots.py` – visualization of trends

---

### results (plots)/

Generated outputs and visualizations.

  - `fft_compare_plots/` – comparison of manual FFT and NumPy FFT
  - `fft_plots/` – frequency spectra
  - `fsc_plots/` – frequency-selective characteristics
  - `trends_results/time_features/` – trend analysis results for time-domain features

---

### main/

Core pipeline execution.

  - `main.py` – entry point of the project
  - `process_file.py` – processes a single signal through the full pipeline
  - `results_exporter.py` – saves computed features and results to files (e.g., CSV)

---

## Team Video Presentations

Each team member prepared an individual video presentation:

- Daryna Prytula – [Watch video](https://www.youtube.com/watch?v=ToF68OirBHk)
- Sofiia Pereima – [Watch video](https://youtu.be/V23egEHX_H0)
- Bohdana Zubrytska – [Watch video](https://youtu.be/uYoiu0prEwA?si=fYNYHlaT13hsdP0O)
