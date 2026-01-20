# Fingerprint Binarization Comparison

This project applies various binarization techniques to fingerprint images and compares the results.

## Implemented Binarization Techniques
1. **Global Thresholding**: Uses a fixed threshold value for the entire image.
2. **Mean Adaptive Thresholding**: Calculates the threshold for a pixel based on the mean of its neighborhood.
3. **Gaussian Adaptive Thresholding**: Calculates the threshold for a pixel based on the Gaussian-weighted sum of its neighborhood.
4. **Otsu's Method**: Automatically determines the optimal global threshold by maximizing inter-class variance.
5. **Niblack's Method**: A local thresholding method that considers the local mean and standard deviation.
6. **Sauvola's Method**: An improvement over Niblack's method, better suited for images with varying illumination.

## Project Structure
- `data/`: Contains the fingerprint datasets (DB1_B, DB2_B, DB3_B, DB4_B).
- `src/binarization.py`: Implementation of the binarization algorithms.
- `main.py`: Main script to process images and generate comparison plots.
- `outputs/`: Directory where comparison results are saved.

## Requirements
Install the required dependencies using:
```bash
pip install -r requirements.txt
```

## How to Run
Run the main script to generate comparisons for all images and create an HTML report:
```bash
python3 main.py
```
The results will be stored in the `outputs/` directory. Open `outputs/index.html` in your web browser to view the consolidated report.
