import numpy as np

def extract_minutiae(thinned_image):
    """
    Extracts minutiae points using the Crossing Number (CN) method.
    The input image should be a thinned skeleton (0 or 255).
    """
    img = (thinned_image > 0).astype(np.int32)
    rows, cols = img.shape
    minutiae = []

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if img[r, c] == 1:
                # Neighbors in clockwise order
                # P9 P2 P3
                # P8 P  P4
                # P7 P6 P5
                p2 = img[r-1, c]
                p3 = img[r-1, c+1]
                p4 = img[r, c+1]
                p5 = img[r+1, c+1]
                p6 = img[r+1, c]
                p7 = img[r+1, c-1]
                p8 = img[r, c-1]
                p9 = img[r-1, c-1]
                
                # Crossing Number: CN = 0.5 * sum(|Pi - Pi+1|) for i=2..9, P10=P2
                cn = 0.5 * (
                    abs(p2 - p3) + abs(p3 - p4) + abs(p4 - p5) + abs(p5 - p6) +
                    abs(p6 - p7) + abs(p7 - p8) + abs(p8 - p9) + abs(p9 - p2)
                )
                
                if cn == 1:
                    minutiae.append({'x': c, 'y': r, 'type': 'Termination'})
                elif cn == 3:
                    minutiae.append({'x': c, 'y': r, 'type': 'Bifurcation'})
                    
    return minutiae
