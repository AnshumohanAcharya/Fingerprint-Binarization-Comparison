"""
Enhanced Database Utilities
Provides additional functions for database analysis and template inspection
"""
import sqlite3
import json
import numpy as np
from collections import defaultdict


def analyze_database(db_path='outputs/fingerprints.db'):
    """
    Analyze the fingerprint database and provide statistics.

    Returns:
        Dictionary with database statistics
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM fingerprints")
    total_count = cursor.fetchone()[0]

    # Get all templates
    cursor.execute("SELECT id, template FROM fingerprints")

    minutiae_counts = []
    persons = defaultdict(int)
    termination_counts = []
    bifurcation_counts = []

    for row in cursor.fetchall():
        fp_id = row[0]
        template = json.loads(row[1])

        # Count minutiae
        minutiae_counts.append(len(template))

        # Count by type
        terminations = sum(1 for m in template if m['type'] == 'Termination')
        bifurcations = sum(1 for m in template if m['type'] == 'Bifurcation')
        termination_counts.append(terminations)
        bifurcation_counts.append(bifurcations)

        # Count samples per person
        person_id = fp_id.split('_')[0]
        persons[person_id] += 1

    conn.close()

    return {
        'total_fingerprints': total_count,
        'total_persons': len(persons),
        'samples_per_person': dict(persons),
        'avg_samples_per_person': np.mean(list(persons.values())),
        'minutiae_stats': {
            'mean': np.mean(minutiae_counts),
            'std': np.std(minutiae_counts),
            'min': np.min(minutiae_counts),
            'max': np.max(minutiae_counts),
            'median': np.median(minutiae_counts)
        },
        'termination_stats': {
            'mean': np.mean(termination_counts),
            'total': sum(termination_counts)
        },
        'bifurcation_stats': {
            'mean': np.mean(bifurcation_counts),
            'total': sum(bifurcation_counts)
        }
    }


def print_database_summary(db_path='outputs/fingerprints.db'):
    """Print a formatted summary of the database."""
    stats = analyze_database(db_path)

    print("\n" + "="*80)
    print(" 📊 FINGERPRINT DATABASE SUMMARY")
    print("="*80 + "\n")

    print(f"Total Fingerprints: {stats['total_fingerprints']}")
    print(f"Total Persons: {stats['total_persons']}")
    print(f"Average Samples per Person: {stats['avg_samples_per_person']:.2f}")

    print("\n" + "-"*80)
    print(" Minutiae Statistics (per fingerprint)")
    print("-"*80)
    print(f"Average: {stats['minutiae_stats']['mean']:.2f}")
    print(f"Std Dev: {stats['minutiae_stats']['std']:.2f}")
    print(f"Min: {stats['minutiae_stats']['min']}")
    print(f"Max: {stats['minutiae_stats']['max']}")
    print(f"Median: {stats['minutiae_stats']['median']:.2f}")

    print("\n" + "-"*80)
    print(" Minutiae Type Distribution")
    print("-"*80)
    print(f"Terminations - Avg per fingerprint: {stats['termination_stats']['mean']:.2f}")
    print(f"Terminations - Total: {stats['termination_stats']['total']}")
    print(f"Bifurcations - Avg per fingerprint: {stats['bifurcation_stats']['mean']:.2f}")
    print(f"Bifurcations - Total: {stats['bifurcation_stats']['total']}")

    print("\n" + "="*80 + "\n")

    return stats


def get_template_quality_scores(db_path='outputs/fingerprints.db'):
    """
    Assign quality scores to templates based on minutiae count.
    Templates with very few minutiae may indicate poor quality images.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, template FROM fingerprints")

    quality_report = []
    for row in cursor.fetchall():
        fp_id = row[0]
        template = json.loads(row[1])
        minutiae_count = len(template)

        # Quality assessment
        if minutiae_count >= 40:
            quality = "Excellent"
        elif minutiae_count >= 25:
            quality = "Good"
        elif minutiae_count >= 15:
            quality = "Fair"
        else:
            quality = "Poor"

        quality_report.append({
            'id': fp_id,
            'minutiae_count': minutiae_count,
            'quality': quality
        })

    conn.close()
    return quality_report


if __name__ == "__main__":
    import sys

    db_path = 'outputs/fingerprints.db'
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    try:
        print_database_summary(db_path)

        # Quality assessment
        quality_scores = get_template_quality_scores(db_path)
        quality_dist = defaultdict(int)
        for item in quality_scores:
            quality_dist[item['quality']] += 1

        print("Quality Distribution:")
        print("-"*80)
        for quality, count in sorted(quality_dist.items()):
            percentage = (count / len(quality_scores)) * 100
            print(f"{quality}: {count} ({percentage:.1f}%)")
        print("-"*80 + "\n")

        # Show poor quality samples if any
        poor_quality = [item for item in quality_scores if item['quality'] == 'Poor']
        if poor_quality:
            print(f"\n⚠️  Found {len(poor_quality)} poor quality templates:")
            for item in poor_quality[:10]:  # Show first 10
                print(f"  - {item['id']}: {item['minutiae_count']} minutiae")
            if len(poor_quality) > 10:
                print(f"  ... and {len(poor_quality) - 10} more")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
