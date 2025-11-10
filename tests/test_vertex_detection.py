"""
Test Vertex Detection Module

This test file visualizes only the vertices where cells meet, without showing
cell segmentation. It displays the original image with vertex markers to show
where multiple cells converge.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cell_segmentation import load_and_validate_images, detect_cells, extract_cell_boundaries
from src.vertex_detection import find_vertices
import config


def main():
    """
    Test the vertex detection module with visualization.
    """
    # Create output directories if they don't exist
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.VISUALIZATION_DIR, exist_ok=True)
    os.makedirs(config.DATA_OUTPUT_DIR, exist_ok=True)
    
    # File paths to process
    image_path = os.path.join(config.DATA_DIR, config.IMAGE_FILE)
    files = [image_path]
    
    # Load images
    imgs = load_and_validate_images(files)
    
    if not imgs:
        print("No images loaded. Exiting.")
        return
    
    # Detect and filter cells
    mask, img, valid_cells, cell_properties = detect_cells(
        imgs, config.CELL_DIAMETER, config.MIN_CELL_AREA, config.MAX_CELL_AREA
    )
    
    # Extract cell boundaries
    cell_boundaries = extract_cell_boundaries(valid_cells, cell_properties)
    
    # Find vertices where cells meet
    vertices = find_vertices(
        valid_cells, cell_boundaries, mask, config.VERTEX_RADIUS, config.MIN_CELLS_FOR_ROSETTE
    )
    
    # ========================================================================
    print("\n" + "="*70)
    print("VERTEX DETECTION TEST RESULTS")
    print("="*70)
    print(f"Total cells detected: {len(valid_cells)}")
    print(f"Total vertices found: {len(vertices)}")
    print("="*70 + "\n")
    
    if len(vertices) > 0:
        print("Vertex Details:")
        print("-" * 80)
        print(f"{'#':<5} {'Location (x,y)':<20} {'Num Cells':<12} {'Cell IDs':<30}")
        print("-" * 80)
        
        for idx, vertex in enumerate(vertices[:20], 1):  # Show first 20
            cell_ids_str = str(vertex['cells'][:5])
            if len(vertex['cells']) > 5:
                cell_ids_str = cell_ids_str[:-1] + ", ...]"
            print(f"{idx:<5} {str(vertex['location']):<20} {vertex['num_cells']:<12} {cell_ids_str:<30}")
        
        if len(vertices) > 20:
            print(f"... and {len(vertices) - 20} more vertices")
    
    # ========================================================================
    print("\n" + "="*70)
    print("VERTEX DETECTION TEST VISUALIZATION")
    print("="*70)
    
    # Create visualization - just original image with vertices marked
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    
    # Show original image
    ax.imshow(img, cmap='gray')
    
    # Mark all vertices
    for idx, vertex in enumerate(vertices, 1):
        x, y = vertex['location']
        # Large red star for vertex
        ax.plot(x, y, 'r*', markersize=15, markeredgewidth=2, markeredgecolor='white')
        # Circle showing vertex radius
        circle = plt.Circle((x, y), config.VERTEX_RADIUS, color='red', fill=False, linewidth=2, linestyle='--', alpha=0.6)
        ax.add_patch(circle)
        # Label with number of cells
        ax.text(x, y-25, f"V{idx}\n({vertex['num_cells']} cells)", 
               color='red', fontsize=8, ha='center', weight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='red'))
    
    ax.set_title(f'Vertex Detection Results\n({len(vertices)} vertices where {config.MIN_CELLS_FOR_ROSETTE}+ cells meet)', 
                fontsize=14, weight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save to output directory
    output_path = os.path.join(config.VISUALIZATION_DIR, 'test_vertex_detection_results.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved as '{output_path}'")
    plt.show()
    
    # Save detailed data
    data_path = os.path.join(config.DATA_OUTPUT_DIR, 'test_vertex_detection_data.txt')
    with open(data_path, 'w') as f:
        f.write(f"VERTEX DETECTION TEST RESULTS\n")
        f.write(f"{'='*80}\n")
        f.write(f"Parameters:\n")
        f.write(f"  Cell diameter: {config.CELL_DIAMETER}\n")
        f.write(f"  Min cell area: {config.MIN_CELL_AREA}\n")
        f.write(f"  Max cell area: {config.MAX_CELL_AREA}\n")
        f.write(f"  Vertex radius: {config.VERTEX_RADIUS}\n")
        f.write(f"  Min cells for vertex: {config.MIN_CELLS_FOR_ROSETTE}\n")
        f.write(f"\nResults:\n")
        f.write(f"  Total cells: {len(valid_cells)}\n")
        f.write(f"  Total vertices: {len(vertices)}\n")
        f.write(f"\n{'='*80}\n\n")
        
        for idx, vertex in enumerate(vertices, 1):
            f.write(f"Vertex {idx}:\n")
            f.write(f"  Location: {vertex['location']}\n")
            f.write(f"  Number of cells: {vertex['num_cells']}\n")
            f.write(f"  Cell IDs: {vertex['cells']}\n\n")
    
    print(f"Data saved to '{data_path}'")
    print("\n" + "="*70)
    print("VERTEX DETECTION TEST COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()
