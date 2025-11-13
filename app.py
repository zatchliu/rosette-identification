"""
Interactive Rosette Detection and Visualization - Main Application

This is the main application file that orchestrates the complete rosette detection
workflow by importing and coordinating the modular components:
- cell_segmentation: Loads images and detects individual cells
- vertex_detection: Finds points where multiple cells meet
- rosette_detection: Clusters vertices and creates visualizations

Author: Rosette Identification Team
Date: November 2025
"""

from src.cell_segmentation import load_and_validate_images, detect_cells, extract_cell_boundaries
from src.vertex_detection import find_vertices
from src.rosette_detection import cluster_vertices, create_base_visualization, prepare_interactive_data, generate_html_visualization
import config

# ============================================================================
# ADJUSTABLE PARAMETERS
# These parameters control the detection sensitivity and filtering criteria
# ============================================================================
CELL_DIAMETER = 30              # Estimated cell diameter for CellPose detection (pixels)
MIN_CELL_AREA = 100             # Minimum area to count as valid cell (pixels)
MAX_CELL_AREA = 5000            # Maximum area to count as valid cell (pixels)
VERTEX_RADIUS = 15              # Search radius for cells meeting at a vertex (pixels)
MIN_CELLS_FOR_ROSETTE = 5       # Minimum cells required to form a rosette
# ============================================================================


def main():
    """
    Main execution function for rosette detection and visualization.
    
    Orchestrates the complete workflow:
    1. Load and validate images
    2. Detect individual cells with CellPose
    3. Extract cell boundaries
    4. Find vertices where cells meet
    5. Cluster vertices into rosettes
    6. Create interactive HTML visualization
    """
    # File paths to process
    import os
    image_path = os.path.join(config.DATA_DIR, config.IMAGE_FILE)
    files = [image_path]   
     
    # Load images
    imgs = load_and_validate_images(files)
    
    if not imgs:
        print("No images loaded. Exiting.")
        return
    
    # Detect and filter cells
    mask, img, valid_cells, cell_properties = detect_cells(
        imgs, CELL_DIAMETER, MIN_CELL_AREA, MAX_CELL_AREA
    )
    
    # Extract cell boundaries
    cell_boundaries = extract_cell_boundaries(valid_cells, cell_properties)
    
    # Find vertices where cells meet
    vertices = find_vertices(
        valid_cells, cell_boundaries, mask, VERTEX_RADIUS, MIN_CELLS_FOR_ROSETTE
    )
    
    # Cluster nearby vertices into rosettes
    rosettes = cluster_vertices(vertices, VERTEX_RADIUS)
    
    num_rosettes = len(rosettes)
    
    # Print results summary
    print("\n" + "="*70)
    print("ROSETTE DETECTION RESULTS")
    print("="*70)
    print(f"Total cells detected: {len(valid_cells)}")
    print(f"Total rosettes found: {num_rosettes}")
    print("="*70 + "\n")
    
    if num_rosettes > 0:
        print("Rosette Details:")
        print("-" * 80)
        print(f"{'#':<5} {'Center (x,y)':<20} {'Num Cells':<12} {'Cell IDs':<30}")
        print("-" * 80)
        
        for idx, rosette in enumerate(rosettes, 1):
            cell_ids_str = str(rosette['cells'][:5])  # Show first 5 cell IDs
            if len(rosette['cells']) > 5:
                cell_ids_str = cell_ids_str[:-1] + ", ...]"
            print(f"{idx:<5} {str(rosette['location']):<20} {rosette['num_cells']:<12} {cell_ids_str:<30}")
    
    # Create interactive visualization
    print("\n" + "="*70)
    print("STEP 5: CREATING INTERACTIVE VISUALIZATION")
    print("="*70)
    
    # Generate base visualization image
    base_img_base64 = create_base_visualization(img, valid_cells, cell_properties, rosettes)
    
    # Prepare data for JavaScript
    print("Creating pixel-to-cell mapping...")
    cell_pixels, rosette_data, cell_to_rosettes = prepare_interactive_data(
        valid_cells, cell_properties, rosettes
    )
    print(f"Prepared data for {len(cell_pixels)} cells in rosettes")
    
    # Generate HTML file
    html_content = generate_html_visualization(
        base_img_base64, cell_pixels, rosette_data, cell_to_rosettes,
        len(valid_cells), num_rosettes
    )
    
    # Save HTML file
    output_file = 'interactive_rosette_viewer.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n{'='*70}")
    print(f"Interactive visualization created: {output_file}")
    print(f"Open this file in your web browser to interact with the rosettes!")
    print(f"{'='*70}")


# Execute main function
if __name__ == "__main__":
    main()