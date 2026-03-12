# Fingerprint Authentication System with EER Analysis

This project implements a complete fingerprint authentication system including binarization, minutiae extraction, matching, and comprehensive performance evaluation with Equal Error Rate (EER) calculation.

## 🎯 Project Overview

This system demonstrates a full biometric authentication pipeline:
1. **Fingerprint Acquisition & Processing**: Binarization and enhancement
2. **Feature Extraction**: Minutiae detection from fingerprint ridges
3. **Template Storage**: SQLite database for fingerprint templates
4. **Matching & Authentication**: Template comparison with configurable thresholds
5. **Performance Evaluation**: FAR, FRR, and EER analysis with optimal threshold determination

## 📋 Implemented Binarization Techniques
1. **Global Thresholding**: Uses a fixed threshold value for the entire image.
2. **Mean Adaptive Thresholding**: Calculates the threshold for a pixel based on the mean of its neighborhood.
3. **Gaussian Adaptive Thresholding**: Calculates the threshold for a pixel based on the Gaussian-weighted sum of its neighborhood.
4. **Otsu's Method**: Automatically determines the optimal global threshold by maximizing inter-class variance.
5. **Niblack's Method**: A local thresholding method that considers the local mean and standard deviation.
6. **Sauvola's Method**: An improvement over Niblack's method, better suited for images with varying illumination.

## 🔬 Advanced Fingerprint Processing
After binarization, the project performs:
1. **Skeletonization (Thinning)**: Applying **Hilditch's Algorithm** to obtain a single-pixel wide representation of the fingerprint ridges.
2. **Minutiae Extraction**: Identifying ridge terminations and bifurcations using the **Crossing Number (CN) method**.
3. **Database Storage**: Extracted minutiae (templates) and image paths are stored in an **SQLite database** (`outputs/fingerprints.db`) with unique IDs for each fingerprint.

## 🔐 Fingerprint Authentication & Evaluation

### Matching Algorithms
The system implements multiple matching methods:
- **Chamfer Distance**: Symmetric average of minimum distances between minutiae sets
- **Hausdorff Distance**: Modified Hausdorff for robust matching
- **Count Match**: Counts matching minutiae within a threshold distance

### Performance Metrics
- **FAR (False Acceptance Rate)**: Probability of accepting an impostor
- **FRR (False Rejection Rate)**: Probability of rejecting a genuine user
- **EER (Equal Error Rate)**: The rate where FAR = FRR (optimal operating point)
- **ROC Curve**: True Acceptance Rate vs False Acceptance Rate
- **DET Curve**: Detection Error Tradeoff curve

### Evaluation Features
- Automatic calculation of optimal threshold
- Comprehensive visualization of score distributions
- FAR/FRR trade-off curves
- Performance tables at multiple threshold values
- Statistical analysis of genuine and impostor scores

## 📁 Project Structure
```
├── data/                          # Fingerprint datasets
│   ├── DB1_B/                     # Database 1
│   ├── DB2_B/                     # Database 2
│   ├── DB3_B/                     # Database 3
│   └── DB4_B/                     # Database 4
├── src/
│   ├── binarization.py            # Binarization algorithms
│   ├── thinning.py                # Hilditch's and Zhang-Suen thinning
│   ├── minutiae.py                # Minutiae extraction (CN method)
│   ├── database.py                # SQLite database operations
│   └── matching.py                # Fingerprint matching & evaluation
├── outputs/
│   ├── fingerprints.db            # SQLite database with templates
│   ├── authentication_evaluation/ # Evaluation results & reports
│   ├── DB*_B/                     # Processed fingerprint visualizations
│   └── index.html                 # Main results index
├── main.py                        # Fingerprint processing pipeline
├── evaluate_authentication.py     # Authentication evaluation & EER analysis
└── requirements.txt               # Python dependencies
```

## 🚀 Requirements
Install the required dependencies using:
```bash
pip install -r requirements.txt
```

**Dependencies:**
- opencv-python-headless
- numpy
- matplotlib
- scikit-image
- scipy
- seaborn

## 📖 How to Run

### Step 1: Process Fingerprints and Extract Features
Run the main script to process all fingerprints, extract minutiae, and store templates:
```bash
python3 main.py
```
This will:
- Apply all binarization techniques to fingerprint images
- Extract minutiae from processed images
- Store templates in SQLite database (`outputs/fingerprints.db`)
- Generate visual comparison reports in `outputs/`

### Step 2: Evaluate Authentication System
Run the evaluation script to calculate EER and optimal threshold:
```bash
python3 evaluate_authentication.py
```
This will:
- Perform genuine and impostor matching comparisons
- Calculate FAR and FRR at various thresholds
- Determine the Equal Error Rate (EER) and optimal threshold
- Generate comprehensive visualizations and reports
- Save results to `outputs/authentication_evaluation/`

### Step 3: View Results
Open the evaluation report in your browser:
```bash
open outputs/authentication_evaluation/authentication_evaluation_report.html
```

Or view the main fingerprint processing results:
```bash
open outputs/index.html
```

## 📊 Understanding the Results

### Equal Error Rate (EER)
The EER is a key metric for biometric system performance. It represents the point where:
- **FAR (False Acceptance Rate) = FRR (False Rejection Rate)**

A **lower EER indicates better system performance**. Typical EER values:
- < 1%: Excellent performance
- 1-5%: Good performance
- 5-10%: Acceptable performance
- > 10%: Poor performance

### Optimal Threshold
The optimal threshold is determined at the EER point. This threshold provides the best balance between:
- **Security**: Preventing unauthorized access (low FAR)
- **Usability**: Minimizing false rejections (low FRR)

### Adjusting for Your Use Case
- **High-security applications**: Use threshold < optimal (lower FAR, higher FRR)
- **User-convenience applications**: Use threshold > optimal (lower FRR, higher FAR)

## 📈 Generated Visualizations

The evaluation generates:
1. **Score Distribution Histogram**: Shows separation between genuine and impostor scores
2. **FAR/FRR Curves**: Illustrates the trade-off at different thresholds
3. **ROC Curve**: Receiver Operating Characteristic curve
4. **DET Curve**: Detection Error Tradeoff curve (log scale)
5. **Performance Table**: Detailed metrics at multiple thresholds
6. **Comprehensive HTML Report**: Interactive report with all results

## 🔍 Dataset Information
The project uses the FVC (Fingerprint Verification Competition) database format with multiple samples per person, enabling both:
- **Genuine matching**: Same person, different samples
- **Impostor matching**: Different persons

## 📝 Notes
- The system uses Sauvola's binarization method as the default for best results
- Minutiae templates are stored as JSON in the SQLite database
- The evaluation performs extensive comparisons; processing time scales with dataset size
- Results are reproducible with fixed random seed for impostor sampling

## 🤝 Contributing
Feel free to enhance the system with:
- Additional matching algorithms
- More sophisticated minutiae descriptors
- Enhanced preprocessing techniques
- Different distance metrics

## 📄 License
This project is for educational and research purposes.
The results will be stored in the `outputs/` directory. Open `outputs/index.html` in your web browser to view the consolidated report.

---

## Secure Encryption Prototype

A second set of utilities implements a **fuzzy commitment** scheme for
fingerprint‑based file encryption.  You can enroll a document by binding a
random AES key to a fingerprint image, then decrypt it later only if the same
(or sufficiently similar) fingerprint is presented.

### Modules
* `src/biometric.py` – extract minutiae points and convert them to a fixed‑size
  binary template.
* `src/fuzzy_commitment.py` – bind a key to a template and recover it using
  Reed‑Solomon error correction.
* `src/crypto.py` – simple AES‑GCM file encryption/decryption.
* `src/secure_system.py` – command‑line wrapper for enrollment and verification.

### Requirements
The encryption prototype adds two new dependencies:
```
pycryptodome
reedsolo
```
which are included in `requirements.txt`.

### Usage
Enroll a file:
```bash
python3 -m src.secure_system enroll \
    --fingerprint data/DB1_B/101_1.tif \
    --infile secret.pdf \
    --outfile secret.enc \
    --helper helper.json
```

Later, present a fingerprint to decrypt:
```bash
python3 -m src.secure_system verify \
    --fingerprint data/DB1_B/101_1.tif \
    --helper helper.json \
    --encrypted secret.enc \
    --out recovered.pdf
```

A demonstration notebook (`fuzzy_commitment_demo.ipynb`) shows the full
workflow on the sample dataset; open it in Jupyter or VS Code.

