import cv2
import os
import matplotlib.pyplot as plt
from src.binarization import (
    global_threshold,
    mean_adaptive_threshold,
    gaussian_adaptive_threshold,
    otsu_threshold,
    niblack_threshold,
    sauvola_threshold
)

def process_and_compare(image_path, output_dir):
    """
    Processes a single image using all binarization techniques and saves a comparison plot.
    """
    img_name = os.path.basename(image_path)
    # Load image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return

    # Apply binarization techniques
    results = {
        "Original": image,
        "Global": global_threshold(image),
        "Mean Adaptive": mean_adaptive_threshold(image),
        "Gaussian Adaptive": gaussian_adaptive_threshold(image),
        "Otsu's": otsu_threshold(image),
        "Niblack's": niblack_threshold(image),
        "Sauvola's": sauvola_threshold(image)
    }

    # Create comparison plot
    fig, axes = plt.subplots(2, 4, figsize=(20, 12))
    fig.suptitle(f"Binarization Comparison - {img_name}", fontsize=20)
    axes = axes.ravel()

    for i, (title, result_img) in enumerate(results.items()):
        axes[i].imshow(result_img, cmap='gray')
        axes[i].set_title(title, fontsize=14)
        axes[i].axis('off')

    # Hide unused subplot
    for i in range(len(results), len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    output_filename = f"comparison_{img_name.split('.')[0]}.png"
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path)
    plt.close()
    print(f"Saved comparison for {img_name} to {output_path}")
    return output_filename

def generate_html_report(dataset_name, output_dir, comparison_images):
    """
    Generates an HTML report to view all comparison images for a dataset.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Binarization Report - {dataset_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #333; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .card {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 45%; min-width: 400px; }}
            .card img {{ width: 100%; display: block; }}
            .card-title {{ padding: 10px; background: #333; color: #fff; text-align: center; font-weight: bold; }}
            @media (max-width: 800px) {{ .card {{ width: 95%; }} }}
        </style>
    </head>
    <body>
        <h1>Binarization Comparison Report - {dataset_name}</h1>
        <div class="container">
    """

    for img in comparison_images:
        title = img.replace("comparison_", "").replace(".png", "")
        html_content += f"""
            <div class="card">
                <div class="card-title">{title}</div>
                <img src="{img}" alt="{title}">
            </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """
    
    report_path = os.path.join(output_dir, "report.html")
    with open(report_path, "w") as f:
        f.write(html_content)
    print(f"Generated HTML report: {report_path}")

def main():
    data_dir = "data"
    output_base_dir = "outputs"
    os.makedirs(output_base_dir, exist_ok=True)

    # We will process all images from each dataset
    datasets = ["DB1_B", "DB2_B", "DB3_B", "DB4_B"]
    
    all_reports = []

    for ds in datasets:
        ds_path = os.path.join(data_dir, ds)
        if not os.path.exists(ds_path):
            print(f"Dataset directory {ds_path} not found.")
            continue
            
        # Get all .tif images in the directory
        images = sorted([f for f in os.listdir(ds_path) if f.endswith('.tif')])
        if not images:
            print(f"No .tif images found in {ds_path}")
            continue
            
        print(f"Processing {len(images)} images from {ds}...")
        ds_output_dir = os.path.join(output_base_dir, ds)
        os.makedirs(ds_output_dir, exist_ok=True)
        
        comparison_images = []
        for sample_image in images:
            image_path = os.path.join(ds_path, sample_image)
            output_img = process_and_compare(image_path, ds_output_dir)
            if output_img:
                comparison_images.append(output_img)
        
        generate_html_report(ds, ds_output_dir, comparison_images)
        all_reports.append((ds, os.path.join(ds, "report.html")))

    # Generate a main index file
    index_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fingerprint Binarization Comparison - Index</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px; text-align: center; }
            h1 { color: #333; }
            .links { display: flex; flex-direction: column; align-items: center; gap: 15px; margin-top: 30px; }
            a { text-decoration: none; color: #fff; background-color: #007bff; padding: 15px 30px; border-radius: 5px; font-weight: bold; width: 200px; transition: background 0.3s; }
            a:hover { background-color: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Fingerprint Binarization Comparison Reports</h1>
        <div class="links">
    """
    for ds, report_link in all_reports:
        index_html += f'        <a href="{report_link}">View {ds} Report</a>\n'
    
    index_html += """
        </div>
    </body>
    </html>
    """
    
    index_path = os.path.join(output_base_dir, "index.html")
    with open(index_path, "w") as f:
        f.write(index_html)
    print(f"Generated main index: {index_path}")

if __name__ == "__main__":
    main()
