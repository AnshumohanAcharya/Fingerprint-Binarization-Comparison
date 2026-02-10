"""
Fingerprint Authentication System Evaluation
Calculates FAR, FRR, EER and finds optimal threshold
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from src.matching import (
    perform_matching_evaluation,
    find_optimal_threshold
)

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def plot_score_distributions(genuine_scores, impostor_scores, method, output_dir):
    """Plot histograms of genuine and impostor score distributions."""
    plt.figure(figsize=(12, 6))

    bins = 50
    plt.hist(genuine_scores, bins=bins, alpha=0.6, label='Genuine Matches',
             color='green', edgecolor='black', density=True)
    plt.hist(impostor_scores, bins=bins, alpha=0.6, label='Impostor Matches',
             color='red', edgecolor='black', density=True)

    plt.xlabel('Similarity Score', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.title(f'Score Distribution - {method.upper()} Method', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    output_path = os.path.join(output_dir, f'score_distribution_{method}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved score distribution plot: {output_path}")


def plot_far_frr_curves(thresholds, far_values, frr_values, eer, eer_threshold,
                        method, output_dir):
    """Plot FAR and FRR curves with EER point marked."""
    plt.figure(figsize=(14, 8))

    # Plot FAR and FRR
    plt.plot(thresholds, far_values * 100, 'r-', linewidth=2.5, label='FAR (False Acceptance Rate)')
    plt.plot(thresholds, frr_values * 100, 'b-', linewidth=2.5, label='FRR (False Rejection Rate)')

    # Mark EER point
    plt.plot(eer_threshold, eer * 100, 'go', markersize=12,
             label=f'EER = {eer*100:.2f}% @ threshold = {eer_threshold:.2f}',
             markeredgecolor='black', markeredgewidth=1.5)

    # Add vertical line at EER threshold
    plt.axvline(x=eer_threshold, color='green', linestyle='--', alpha=0.7, linewidth=1.5)

    plt.xlabel('Threshold Value', fontsize=13, fontweight='bold')
    plt.ylabel('Error Rate (%)', fontsize=13, fontweight='bold')
    plt.title(f'FAR vs FRR Trade-off Curve - {method.upper()} Method',
              fontsize=15, fontweight='bold')
    plt.legend(fontsize=11, loc='best')
    plt.grid(True, alpha=0.3)

    # Add text box with statistics
    textstr = f'Optimal Threshold: {eer_threshold:.4f}\nEER: {eer*100:.4f}%'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', bbox=props)

    output_path = os.path.join(output_dir, f'far_frr_curves_{method}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved FAR/FRR curves: {output_path}")


def plot_roc_curve(far_values, frr_values, eer, method, output_dir):
    """Plot ROC (Receiver Operating Characteristic) curve."""
    plt.figure(figsize=(10, 10))

    # TAR (True Acceptance Rate) = 1 - FRR
    tar_values = 1 - frr_values

    plt.plot(far_values * 100, tar_values * 100, 'b-', linewidth=2.5)
    plt.plot([0, 100], [100, 0], 'r--', linewidth=1.5, alpha=0.7, label='EER Line')

    # Mark EER point
    eer_idx = np.argmin(np.abs(far_values - frr_values))
    plt.plot(far_values[eer_idx] * 100, tar_values[eer_idx] * 100, 'go',
             markersize=12, label=f'EER = {eer*100:.2f}%',
             markeredgecolor='black', markeredgewidth=1.5)

    plt.xlabel('FAR - False Acceptance Rate (%)', fontsize=13, fontweight='bold')
    plt.ylabel('TAR - True Acceptance Rate (%)', fontsize=13, fontweight='bold')
    plt.title(f'ROC Curve - {method.upper()} Method', fontsize=15, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 100])
    plt.ylim([0, 100])

    output_path = os.path.join(output_dir, f'roc_curve_{method}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved ROC curve: {output_path}")


def plot_det_curve(far_values, frr_values, eer, method, output_dir):
    """Plot DET (Detection Error Tradeoff) curve."""
    plt.figure(figsize=(10, 10))

    # DET curve uses log scale
    plt.plot(far_values * 100, frr_values * 100, 'b-', linewidth=2.5)

    # Mark EER point
    eer_idx = np.argmin(np.abs(far_values - frr_values))
    plt.plot(far_values[eer_idx] * 100, frr_values[eer_idx] * 100, 'go',
             markersize=12, label=f'EER = {eer*100:.2f}%',
             markeredgecolor='black', markeredgewidth=1.5)

    plt.xlabel('FAR - False Acceptance Rate (%)', fontsize=13, fontweight='bold')
    plt.ylabel('FRR - False Rejection Rate (%)', fontsize=13, fontweight='bold')
    plt.title(f'DET Curve - {method.upper()} Method', fontsize=15, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, which='both')
    plt.xscale('log')
    plt.yscale('log')

    output_path = os.path.join(output_dir, f'det_curve_{method}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved DET curve: {output_path}")


def create_performance_table(evaluation_results, output_dir):
    """Create a table showing performance metrics at different thresholds."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')

    # Select representative thresholds
    results = evaluation_results['results']
    step = max(1, len(results) // 20)  # Show ~20 rows
    selected_results = results[::step]

    table_data = []
    for r in selected_results:
        table_data.append([
            f"{r['threshold']:.4f}",
            f"{r['FAR']*100:.2f}%",
            f"{r['FRR']*100:.2f}%"
        ])

    table = ax.table(cellText=table_data,
                     colLabels=['Threshold', 'FAR (%)', 'FRR (%)'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.3, 0.3, 0.3])

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style header
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(3):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    plt.title(f'Performance Metrics at Different Thresholds\n{evaluation_results["method"].upper()} Method',
              fontsize=14, fontweight='bold', pad=20)

    output_path = os.path.join(output_dir, f'performance_table_{evaluation_results["method"]}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved performance table: {output_path}")


def generate_comprehensive_report(evaluation_data, optimal_data, method, output_dir):
    """Generate a comprehensive HTML report with all results."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fingerprint Authentication System - Evaluation Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                color: #333;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2.5em;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .subtitle {{
                text-align: center;
                color: #7f8c8d;
                margin-bottom: 40px;
                font-size: 1.2em;
            }}
            .summary-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 40px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .summary-box h2 {{
                margin-bottom: 20px;
                font-size: 1.8em;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .metric-card {{
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 8px;
                border: 2px solid rgba(255,255,255,0.3);
            }}
            .metric-card h3 {{
                font-size: 0.9em;
                margin-bottom: 10px;
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
            }}
            .section {{
                margin-bottom: 50px;
            }}
            .section h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
                font-size: 1.8em;
            }}
            .image-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 30px;
                margin-top: 20px;
            }}
            .image-card {{
                background: #f8f9fa;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .image-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            }}
            .image-card img {{
                width: 100%;
                display: block;
            }}
            .image-caption {{
                padding: 15px;
                text-align: center;
                font-weight: bold;
                color: #2c3e50;
                background: white;
            }}
            .info-box {{
                background: #e8f4f8;
                border-left: 5px solid #3498db;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .info-box h3 {{
                color: #2980b9;
                margin-bottom: 10px;
            }}
            .info-box p {{
                line-height: 1.6;
                color: #34495e;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                color: #7f8c8d;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: center;
                border: 1px solid #ddd;
            }}
            th {{
                background: #667eea;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Fingerprint Authentication System</h1>
            <div class="subtitle">Equal Error Rate (EER) Analysis & Optimal Threshold Determination</div>
            
            <div class="summary-box">
                <h2>📊 Key Performance Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Matching Method</h3>
                        <div class="metric-value">{method.upper()}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Equal Error Rate (EER)</h3>
                        <div class="metric-value">{optimal_data['eer']*100:.3f}%</div>
                    </div>
                    <div class="metric-card">
                        <h3>Optimal Threshold</h3>
                        <div class="metric-value">{optimal_data['eer_threshold']:.4f}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Total Genuine Comparisons</h3>
                        <div class="metric-value">{len(evaluation_data['genuine_scores'])}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Total Impostor Comparisons</h3>
                        <div class="metric-value">{len(evaluation_data['impostor_scores'])}</div>
                    </div>
                </div>
            </div>

            <div class="info-box">
                <h3>📖 What is EER?</h3>
                <p>
                    The Equal Error Rate (EER) is the point where the False Acceptance Rate (FAR) 
                    equals the False Rejection Rate (FRR). It provides a single metric to evaluate 
                    the overall performance of a biometric system. A lower EER indicates better system 
                    performance. The threshold at EER represents the optimal operating point that 
                    balances security (preventing false acceptances) and usability (preventing false rejections).
                </p>
            </div>

            <div class="section">
                <h2>📈 Score Distributions</h2>
                <p style="margin-bottom: 20px; line-height: 1.6;">
                    The histogram below shows the distribution of similarity scores for genuine matches 
                    (same finger) and impostor matches (different fingers). Good separation between 
                    these distributions indicates a more effective matching algorithm.
                </p>
                <div class="image-grid">
                    <div class="image-card">
                        <img src="score_distribution_{method}.png" alt="Score Distribution">
                        <div class="image-caption">Genuine vs Impostor Score Distribution</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📉 FAR vs FRR Trade-off</h2>
                <p style="margin-bottom: 20px; line-height: 1.6;">
                    This curve illustrates the fundamental trade-off in biometric systems: as we decrease 
                    the threshold to reduce false rejections (FRR), we increase false acceptances (FAR), 
                    and vice versa. The optimal operating point (EER) is where these two error rates meet.
                </p>
                <div class="image-grid">
                    <div class="image-card">
                        <img src="far_frr_curves_{method}.png" alt="FAR FRR Curves">
                        <div class="image-caption">FAR and FRR vs Threshold</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📊 ROC and DET Curves</h2>
                <p style="margin-bottom: 20px; line-height: 1.6;">
                    The Receiver Operating Characteristic (ROC) curve plots True Acceptance Rate vs 
                    False Acceptance Rate. The Detection Error Tradeoff (DET) curve plots FAR vs FRR 
                    on a log scale, providing better visibility of performance at low error rates.
                </p>
                <div class="image-grid">
                    <div class="image-card">
                        <img src="roc_curve_{method}.png" alt="ROC Curve">
                        <div class="image-caption">ROC Curve</div>
                    </div>
                    <div class="image-card">
                        <img src="det_curve_{method}.png" alt="DET Curve">
                        <div class="image-caption">DET Curve</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📋 Performance Table</h2>
                <p style="margin-bottom: 20px; line-height: 1.6;">
                    Detailed performance metrics at various threshold values, showing how FAR and FRR 
                    change as the decision threshold is adjusted.
                </p>
                <div class="image-card">
                    <img src="performance_table_{method}.png" alt="Performance Table">
                    <div class="image-caption">Performance Metrics at Different Thresholds</div>
                </div>
            </div>

            <div class="info-box">
                <h3>🎯 Recommendations</h3>
                <p>
                    <strong>Optimal Threshold:</strong> {optimal_data['eer_threshold']:.4f}<br>
                    <strong>Expected EER:</strong> {optimal_data['eer']*100:.3f}%<br><br>
                    
                    For security-critical applications, consider using a threshold slightly below the 
                    optimal value to reduce FAR (increase security) at the cost of slightly higher FRR 
                    (more false rejections). For user-convenience applications, use a threshold slightly 
                    above optimal to reduce FRR at the cost of slightly higher FAR.
                </p>
            </div>

            <div class="footer">
                <p>Generated on: {evaluation_data.get('timestamp', 'N/A')}</p>
                <p>Fingerprint Authentication System Evaluation Report</p>
            </div>
        </div>
    </body>
    </html>
    """

    report_path = os.path.join(output_dir, 'authentication_evaluation_report.html')
    with open(report_path, 'w') as f:
        f.write(html_content)
    print(f"\n✅ Generated comprehensive HTML report: {report_path}")
    return report_path


def save_results_json(evaluation_data, optimal_data, method, output_dir):
    """Save results in JSON format for further analysis."""
    results = {
        'method': method,
        'eer': float(optimal_data['eer']),
        'eer_threshold': float(optimal_data['eer_threshold']),
        'num_genuine_scores': len(evaluation_data['genuine_scores']),
        'num_impostor_scores': len(evaluation_data['impostor_scores']),
        'genuine_score_stats': {
            'mean': float(np.mean(evaluation_data['genuine_scores'])),
            'std': float(np.std(evaluation_data['genuine_scores'])),
            'min': float(np.min(evaluation_data['genuine_scores'])),
            'max': float(np.max(evaluation_data['genuine_scores']))
        },
        'impostor_score_stats': {
            'mean': float(np.mean(evaluation_data['impostor_scores'])),
            'std': float(np.std(evaluation_data['impostor_scores'])),
            'min': float(np.min(evaluation_data['impostor_scores'])),
            'max': float(np.max(evaluation_data['impostor_scores']))
        },
        'sample_thresholds_performance': []
    }

    # Add sample threshold performance
    for result in evaluation_data['results'][::len(evaluation_data['results'])//20]:
        results['sample_thresholds_performance'].append({
            'threshold': float(result['threshold']),
            'far': float(result['FAR']),
            'frr': float(result['FRR'])
        })

    json_path = os.path.join(output_dir, 'evaluation_results.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved JSON results: {json_path}")


def main():
    """Main evaluation function."""
    # Configuration
    db_path = 'outputs/fingerprints.db'
    output_dir = 'outputs/authentication_evaluation'
    os.makedirs(output_dir, exist_ok=True)

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        print("Please run main.py first to process fingerprints and create the database.")
        return

    # Matching methods to evaluate
    methods = ['chamfer']  # Can add 'hausdorff', 'count_match'

    for method in methods:
        print(f"\n{'='*80}")
        print(f"Evaluating {method.upper()} matching method")
        print(f"{'='*80}\n")

        # Generate threshold range
        # For distance-based methods, typical ranges are 10-100 pixels
        if method in ['chamfer', 'hausdorff']:
            test_thresholds = np.linspace(5, 100, 50)
        else:  # count_match
            test_thresholds = np.linspace(0.1, 1.0, 50)

        # Perform matching evaluation
        print("Performing matching evaluation...")
        evaluation_data = perform_matching_evaluation(db_path, test_thresholds, method)

        # Add timestamp
        from datetime import datetime
        evaluation_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Find optimal threshold and EER
        print("\nCalculating optimal threshold and EER...")
        optimal_data = find_optimal_threshold(
            evaluation_data['genuine_scores'],
            evaluation_data['impostor_scores'],
            method
        )

        print(f"\n{'='*60}")
        print(f"RESULTS FOR {method.upper()} METHOD")
        print(f"{'='*60}")
        print(f"Equal Error Rate (EER): {optimal_data['eer']*100:.4f}%")
        print(f"Optimal Threshold: {optimal_data['eer_threshold']:.6f}")
        print(f"Genuine Comparisons: {len(evaluation_data['genuine_scores'])}")
        print(f"Impostor Comparisons: {len(evaluation_data['impostor_scores'])}")
        print(f"{'='*60}\n")

        # Generate visualizations
        print("Generating visualizations...")
        plot_score_distributions(
            evaluation_data['genuine_scores'],
            evaluation_data['impostor_scores'],
            method,
            output_dir
        )

        plot_far_frr_curves(
            optimal_data['all_thresholds'],
            optimal_data['far_values'],
            optimal_data['frr_values'],
            optimal_data['eer'],
            optimal_data['eer_threshold'],
            method,
            output_dir
        )

        plot_roc_curve(
            optimal_data['far_values'],
            optimal_data['frr_values'],
            optimal_data['eer'],
            method,
            output_dir
        )

        plot_det_curve(
            optimal_data['far_values'],
            optimal_data['frr_values'],
            optimal_data['eer'],
            method,
            output_dir
        )

        create_performance_table(evaluation_data, output_dir)

        # Generate comprehensive report
        print("\nGenerating comprehensive report...")
        report_path = generate_comprehensive_report(
            evaluation_data,
            optimal_data,
            method,
            output_dir
        )

        # Save JSON results
        save_results_json(evaluation_data, optimal_data, method, output_dir)

        print(f"\n✅ Evaluation complete for {method.upper()} method!")
        print(f"📁 All results saved to: {output_dir}")
        print(f"🌐 Open the report: {report_path}")


if __name__ == "__main__":
    main()
