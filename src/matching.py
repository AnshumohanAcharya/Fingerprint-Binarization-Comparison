"""
Fingerprint Matching Module
Implements minutiae-based matching with various similarity metrics
"""
import numpy as np
import json
import sqlite3
from scipy.spatial.distance import cdist


def load_template_from_db(conn, fp_id):
    """Load fingerprint template from database."""
    cursor = conn.cursor()
    cursor.execute('SELECT template FROM fingerprints WHERE id = ?', (fp_id,))
    result = cursor.fetchone()
    if result:
        return json.loads(result[0])
    return None


def extract_minutiae_features(minutiae):
    """
    Convert minutiae list to numpy array for matching.
    Returns array of shape (N, 2) with x, y coordinates.
    """
    if not minutiae:
        return np.array([])
    return np.array([[m['x'], m['y']] for m in minutiae])


def calculate_similarity_score(template1, template2, method='hausdorff'):
    """
    Calculate similarity score between two fingerprint templates.

    Args:
        template1: List of minutiae dictionaries from first fingerprint
        template2: List of minutiae dictionaries from second fingerprint
        method: Matching method ('hausdorff', 'chamfer', 'count_match')

    Returns:
        Similarity score (higher means more similar for count_match,
        lower means more similar for distance-based methods)
    """
    points1 = extract_minutiae_features(template1)
    points2 = extract_minutiae_features(template2)

    # Handle empty templates
    if len(points1) == 0 or len(points2) == 0:
        return float('inf') if method in ['hausdorff', 'chamfer'] else 0.0

    if method == 'hausdorff':
        # Modified Hausdorff distance (average of minimum distances)
        dist_matrix = cdist(points1, points2, metric='euclidean')
        forward = np.mean(np.min(dist_matrix, axis=1))
        backward = np.mean(np.min(dist_matrix, axis=0))
        return max(forward, backward)

    elif method == 'chamfer':
        # Chamfer distance (symmetric average)
        dist_matrix = cdist(points1, points2, metric='euclidean')
        forward = np.mean(np.min(dist_matrix, axis=1))
        backward = np.mean(np.min(dist_matrix, axis=0))
        return (forward + backward) / 2

    elif method == 'count_match':
        # Count matching minutiae within a threshold
        match_threshold = 10.0  # pixels
        dist_matrix = cdist(points1, points2, metric='euclidean')
        matches = np.sum(np.min(dist_matrix, axis=1) < match_threshold)
        # Normalize by average number of minutiae
        avg_count = (len(points1) + len(points2)) / 2
        return matches / avg_count if avg_count > 0 else 0.0

    else:
        raise ValueError(f"Unknown matching method: {method}")


def match_fingerprints(template1, template2, threshold, method='chamfer'):
    """
    Match two fingerprint templates and return match decision.

    Args:
        template1: First fingerprint template (minutiae list)
        template2: Second fingerprint template (minutiae list)
        threshold: Decision threshold
        method: Matching method

    Returns:
        True if fingerprints match, False otherwise, and the similarity score
    """
    score = calculate_similarity_score(template1, template2, method)

    # For distance-based methods, lower score means better match
    if method in ['hausdorff', 'chamfer']:
        is_match = score <= threshold
    else:  # count_match
        is_match = score >= threshold

    return is_match, score


def get_all_templates(conn):
    """Retrieve all fingerprint templates from database."""
    cursor = conn.cursor()
    cursor.execute('SELECT id, template FROM fingerprints')
    templates = {}
    for row in cursor.fetchall():
        fp_id = row[0]
        template = json.loads(row[1])
        templates[fp_id] = template
    return templates


def perform_matching_evaluation(db_path, thresholds, method='chamfer'):
    """
    Perform comprehensive matching evaluation across all threshold values.

    This function:
    1. Loads all templates from database
    2. Performs genuine (same finger) and impostor (different fingers) comparisons
    3. Calculates similarity scores for all pairs
    4. Evaluates FAR, FRR for each threshold

    Args:
        db_path: Path to SQLite database
        thresholds: List of threshold values to evaluate
        method: Matching method to use

    Returns:
        Dictionary containing:
        - genuine_scores: List of scores for genuine comparisons
        - impostor_scores: List of scores for impostor comparisons
        - results: List of dicts with threshold, FAR, FRR for each threshold
    """
    conn = sqlite3.connect(db_path)
    templates = get_all_templates(conn)
    conn.close()

    # Parse fingerprint IDs to identify genuine pairs
    # Format: XXX_Y where XXX is person ID and Y is sample number
    fingerprints_by_person = {}
    for fp_id in templates.keys():
        # Extract person ID (e.g., "101" from "101_1")
        person_id = fp_id.split('_')[0]
        if person_id not in fingerprints_by_person:
            fingerprints_by_person[person_id] = []
        fingerprints_by_person[person_id].append(fp_id)

    genuine_scores = []
    impostor_scores = []

    # Calculate genuine scores (same person, different samples)
    print("Calculating genuine match scores...")
    for person_id, fp_ids in fingerprints_by_person.items():
        if len(fp_ids) < 2:
            continue
        # Compare all pairs of samples from the same person
        for i in range(len(fp_ids)):
            for j in range(i + 1, len(fp_ids)):
                score = calculate_similarity_score(
                    templates[fp_ids[i]],
                    templates[fp_ids[j]],
                    method
                )
                genuine_scores.append(score)

    # Calculate impostor scores (different persons)
    print("Calculating impostor match scores...")
    person_ids = list(fingerprints_by_person.keys())
    # To avoid too many comparisons, sample a representative set
    import random
    random.seed(42)

    for i in range(min(len(person_ids), 50)):  # Limit to avoid excessive computation
        for j in range(i + 1, min(len(person_ids), 50)):
            person1_id = person_ids[i]
            person2_id = person_ids[j]
            # Compare first sample from each person
            if fingerprints_by_person[person1_id] and fingerprints_by_person[person2_id]:
                score = calculate_similarity_score(
                    templates[fingerprints_by_person[person1_id][0]],
                    templates[fingerprints_by_person[person2_id][0]],
                    method
                )
                impostor_scores.append(score)

    print(f"Generated {len(genuine_scores)} genuine scores and {len(impostor_scores)} impostor scores")

    # Evaluate FAR and FRR for each threshold
    results = []
    for threshold in thresholds:
        far, frr = calculate_far_frr(genuine_scores, impostor_scores, threshold, method)
        results.append({
            'threshold': threshold,
            'FAR': far,
            'FRR': frr
        })

    return {
        'genuine_scores': genuine_scores,
        'impostor_scores': impostor_scores,
        'results': results,
        'method': method
    }


def calculate_far_frr(genuine_scores, impostor_scores, threshold, method):
    """
    Calculate False Acceptance Rate (FAR) and False Rejection Rate (FRR).

    Args:
        genuine_scores: Scores from genuine comparisons
        impostor_scores: Scores from impostor comparisons
        threshold: Decision threshold
        method: Matching method ('chamfer', 'hausdorff', or 'count_match')

    Returns:
        Tuple of (FAR, FRR)
    """
    genuine_scores = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)

    if method in ['hausdorff', 'chamfer']:
        # For distance-based: accept if score <= threshold
        # FRR: genuine pairs incorrectly rejected (score > threshold)
        false_rejections = np.sum(genuine_scores > threshold)
        frr = false_rejections / len(genuine_scores) if len(genuine_scores) > 0 else 0

        # FAR: impostor pairs incorrectly accepted (score <= threshold)
        false_acceptances = np.sum(impostor_scores <= threshold)
        far = false_acceptances / len(impostor_scores) if len(impostor_scores) > 0 else 0
    else:  # count_match
        # For similarity-based: accept if score >= threshold
        # FRR: genuine pairs incorrectly rejected (score < threshold)
        false_rejections = np.sum(genuine_scores < threshold)
        frr = false_rejections / len(genuine_scores) if len(genuine_scores) > 0 else 0

        # FAR: impostor pairs incorrectly accepted (score >= threshold)
        false_acceptances = np.sum(impostor_scores >= threshold)
        far = false_acceptances / len(impostor_scores) if len(impostor_scores) > 0 else 0

    return far, frr


def find_optimal_threshold(genuine_scores, impostor_scores, method, num_points=1000):
    """
    Find the optimal threshold that minimizes the Equal Error Rate (EER).

    Returns:
        Dictionary containing:
        - eer: Equal Error Rate
        - eer_threshold: Threshold at EER
        - all_thresholds: Array of tested thresholds
        - far_values: Array of FAR values
        - frr_values: Array of FRR values
    """
    # Generate threshold range based on score distributions
    all_scores = np.concatenate([genuine_scores, impostor_scores])
    min_score = np.min(all_scores)
    max_score = np.max(all_scores)

    thresholds = np.linspace(min_score, max_score, num_points)

    far_values = []
    frr_values = []

    for threshold in thresholds:
        far, frr = calculate_far_frr(genuine_scores, impostor_scores, threshold, method)
        far_values.append(far)
        frr_values.append(frr)

    far_values = np.array(far_values)
    frr_values = np.array(frr_values)

    # Find EER (where FAR = FRR)
    diff = np.abs(far_values - frr_values)
    eer_idx = np.argmin(diff)
    eer = (far_values[eer_idx] + frr_values[eer_idx]) / 2
    eer_threshold = thresholds[eer_idx]

    return {
        'eer': eer,
        'eer_threshold': eer_threshold,
        'all_thresholds': thresholds,
        'far_values': far_values,
        'frr_values': frr_values
    }
