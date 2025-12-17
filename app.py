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

import os
import sys
from src.cell_segmentation import load_and_validate_images, detect_cells, extract_cell_boundaries
from src.vertex_detection import find_vertices
from src.rosette_detection import cluster_vertices, create_base_visualization, prepare_interactive_data, generate_html_visualization

# ============================================================================
# DEFAULT PARAMETERS
# These parameters control the detection sensitivity and filtering criteria
# ============================================================================
DEFAULT_CELL_DIAMETER = 30              # Estimated cell diameter for CellPose detection (pixels)
DEFAULT_MIN_CELL_AREA = 100             # Minimum area to count as valid cell (pixels)
DEFAULT_MAX_CELL_AREA = 5000            # Maximum area to count as valid cell (pixels)
DEFAULT_VERTEX_RADIUS = 15              # Search radius for cells meeting at a vertex (pixels)
DEFAULT_MIN_CELLS_FOR_ROSETTE = 5       # Minimum cells required to form a rosette
# ============================================================================


def get_user_input():
    """
    Prompt user for input file and optional parameters.
    
    Returns:
        Dictionary containing all configuration parameters
    """
    print("\n" + "="*70)
    print("ROSETTE DETECTION - INTERACTIVE SETUP")
    print("="*70)
    
    # Get input image file
    while True:
        image_path = input("\nEnter the path to your image file: ").strip()
        
        # Remove quotes if user included them
        image_path = image_path.strip('"').strip("'")
        
        if os.path.exists(image_path):
            print(f"✓ Found image: {image_path}")
            break
        else:
            print(f"✗ File not found: {image_path}")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                print("Exiting...")
                sys.exit(0)
    
    # Ask if user wants to customize parameters
    print("\n" + "-"*70)
    customize = input("\nWould you like to customize detection parameters? (y/n, default: n): ").strip().lower()
    
    if customize == 'y':
        print("\nEnter custom parameters (press Enter to use default):")
        
        # Cell diameter
        diameter_input = input(f"  Cell diameter in pixels (default: {DEFAULT_CELL_DIAMETER}): ").strip()
        cell_diameter = int(diameter_input) if diameter_input else DEFAULT_CELL_DIAMETER
        
        # Min cell area
        min_area_input = input(f"  Minimum cell area in pixels (default: {DEFAULT_MIN_CELL_AREA}): ").strip()
        min_cell_area = int(min_area_input) if min_area_input else DEFAULT_MIN_CELL_AREA
        
        # Max cell area
        max_area_input = input(f"  Maximum cell area in pixels (default: {DEFAULT_MAX_CELL_AREA}): ").strip()
        max_cell_area = int(max_area_input) if max_area_input else DEFAULT_MAX_CELL_AREA
        
        # Vertex radius
        vertex_input = input(f"  Vertex search radius in pixels (default: {DEFAULT_VERTEX_RADIUS}): ").strip()
        vertex_radius = int(vertex_input) if vertex_input else DEFAULT_VERTEX_RADIUS
        
        # Min rosette cells
        rosette_input = input(f"  Minimum cells for rosette (default: {DEFAULT_MIN_CELLS_FOR_ROSETTE}): ").strip()
        min_rosette_cells = int(rosette_input) if rosette_input else DEFAULT_MIN_CELLS_FOR_ROSETTE
    else:
        cell_diameter = DEFAULT_CELL_DIAMETER
        min_cell_area = DEFAULT_MIN_CELL_AREA
        max_cell_area = DEFAULT_MAX_CELL_AREA
        vertex_radius = DEFAULT_VERTEX_RADIUS
        min_rosette_cells = DEFAULT_MIN_CELLS_FOR_ROSETTE
    
    # Get output filename
    print("\n" + "-"*70)
    output_input = input("\nEnter output HTML filename (default: interactive_rosette_viewer.html): ").strip()
    output_file = output_input if output_input else 'interactive_rosette_viewer.html'
    
    # Ensure .html extension
    if not output_file.endswith('.html'):
        output_file += '.html'
    
    return {
        'image_path': image_path,
        'output_file': output_file,
        'cell_diameter': cell_diameter,
        'min_cell_area': min_cell_area,
        'max_cell_area': max_cell_area,
        'vertex_radius': vertex_radius,
        'min_rosette_cells': min_rosette_cells
    }


def main():
    """
    Main execution function for rosette detection and visualization.
    
    Orchestrates the complete workflow:
    1. Prompt user for input file and parameters
    2. Load and validate images
    3. Detect individual cells with CellPose
    4. Extract cell boundaries
    5. Find vertices where cells meet
    6. Cluster vertices into rosettes
    7. Create interactive HTML visualization
    """
    # Get user input
    config = get_user_input()
    
    # Display configuration
    print("\n" + "="*70)
    print("ROSETTE DETECTION CONFIGURATION")
    print("="*70)
    print(f"Input image: {config['image_path']}")
    print(f"Output file: {config['output_file']}")
    print(f"Cell diameter: {config['cell_diameter']} pixels")
    print(f"Cell area range: {config['min_cell_area']} - {config['max_cell_area']} pixels")
    print(f"Vertex radius: {config['vertex_radius']} pixels")
    print(f"Min cells for rosette: {config['min_rosette_cells']}")
    print("="*70 + "\n")
    
    # Confirm to proceed
    proceed = input("Proceed with analysis? (y/n, default: y): ").strip().lower()
    if proceed == 'n':
        print("Analysis cancelled.")
        sys.exit(0)
    
    print("\nStarting analysis...")
    
    # Load images
    files = [config['image_path']]
    imgs = load_and_validate_images(files)
    
    if not imgs:
        print("ERROR: Failed to load image. Exiting.")
        sys.exit(1)
    
    # Detect and filter cells
    mask, img, valid_cells, cell_properties = detect_cells(
        imgs, config['cell_diameter'], config['min_cell_area'], config['max_cell_area']
    )
    
    if len(valid_cells) == 0:
        print("\nERROR: No valid cells detected.")
        print("Suggestions:")
        print("  - Try adjusting the cell diameter parameter")
        print("  - Check min/max area thresholds")
        print("  - Verify image quality and contrast")
        sys.exit(1)
    
    # Extract cell boundaries
    cell_boundaries = extract_cell_boundaries(valid_cells, cell_properties)
    
    # Find vertices where cells meet (using the min_rosette_cells threshold)
    vertices = find_vertices(
        valid_cells, cell_boundaries, mask, config['vertex_radius'], config['min_rosette_cells']
    )
    
    # Cluster nearby vertices into rosettes
    rosettes = cluster_vertices(vertices, config['vertex_radius'], config['min_rosette_cells'])
    
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
    else:
        print("⚠ No rosettes found.")
        print("\nSuggestions:")
        print(f"  - Try decreasing min-rosette-cells (current: {config['min_rosette_cells']})")
        print(f"  - Try increasing vertex-radius (current: {config['vertex_radius']})")
        print(f"  - Adjust cell diameter for better detection (current: {config['cell_diameter']})")
        
        retry = input("\nWould you like to run again with different parameters? (y/n): ").strip().lower()
        if retry == 'y':
            print("\n" + "="*70)
            print("Restarting analysis...")
            print("="*70)
            main()
            return
    
    # Create interactive visualization
    print("\n" + "="*70)
    print("STEP 5: CREATING INTERACTIVE VISUALIZATION")
    print("="*70)
    
    # Generate base visualization image
    base_img_base64 = create_base_visualization(img, valid_cells, cell_properties, rosettes)
    
    # Prepare data for JavaScript (includes all cells and their properties)
    print("Creating pixel-to-cell mapping and calculating cell properties...")
    cell_pixels, cell_data, rosette_data, cell_to_rosettes = prepare_interactive_data(
        valid_cells, cell_properties, cell_boundaries, vertices, rosettes
    )
    print(f"Prepared data for {len(cell_pixels)} total cells")
    print(f"  - Cells in rosettes: {len([c for c in cell_data.values() if c['in_rosette']])}")
    print(f"  - Cells not in rosettes: {len([c for c in cell_data.values() if not c['in_rosette']])}")
    
    # Generate HTML file
    html_content = generate_html_visualization(
        base_img_base64, cell_pixels, cell_data, rosette_data, cell_to_rosettes,
        len(valid_cells), num_rosettes
    )
    
    # Save HTML file
    with open(config['output_file'], 'w') as f:
        f.write(html_content)
    
    print(f"\n{'='*70}")
    print(f"✓ SUCCESS! Interactive visualization created: {config['output_file']}")
    print(f"  Open this file in your web browser to interact with the rosettes!")
    print(f"{'='*70}\n")


# Execute main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: An unexpected error occurred:")
        print(f"  {str(e)}")
        print("\nPlease check your input file and parameters.")
        sys.exit(1)