"""
Interactive Rosette Detection and Visualization - Main Application

This is the main application file that orchestrates the complete rosette detection
workflow by importing and coordinating the modular components:
- cell_segmentation: Loads images and detects individual cells
- vertex_detection: Finds points where multiple cells meet
- rosette_detection: Clusters vertices and creates visualizations
- csv_export: Exports detailed cell properties and junction counts to CSV

"""

import os
import sys
import glob
from pathlib import Path
from src.cell_segmentation import load_and_validate_images, detect_cells, extract_cell_boundaries
from src.vertex_detection import find_vertices
from src.rosette_detection import cluster_vertices, create_base_visualization, prepare_interactive_data, generate_html_visualization, calculate_cell_neighbors
from src.csv_export import generate_csv_export
import config as cfg
import os

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

# Supported image file extensions
IMAGE_EXTENSIONS = {'.tif', '.tiff', '.png', '.jpg', '.jpeg', '.bmp'}


def get_user_input():
    """
    Prompt user for input file/folder and optional parameters.
    
    Returns:
        Dictionary containing all configuration parameters
    """
    print("\n" + "="*70)
    print("ROSETTE DETECTION - INTERACTIVE SETUP")
    print("="*70)
    
    # Ask if processing single file or batch folder
    print("\nProcessing mode:")
    print("  1. Single image file")
    print("  2. Batch process folder")
    
    while True:
        mode_input = input("\nSelect mode (1 or 2, default: 1): ").strip()
        if mode_input == '' or mode_input == '1':
            batch_mode = False
            break
        elif mode_input == '2':
            batch_mode = True
            break
        else:
            print("Invalid input. Please enter 1 or 2.")
    
    # Get input path
    if batch_mode:
        while True:
            folder_path = input("\nEnter the path to your image folder: ").strip()
            folder_path = folder_path.strip('"').strip("'")
            
            if os.path.isdir(folder_path):
                # Find all image files in the folder
                image_files = []
                for ext in IMAGE_EXTENSIONS:
                    image_files.extend(glob.glob(os.path.join(folder_path, f"*{ext}")))
                    image_files.extend(glob.glob(os.path.join(folder_path, f"*{ext.upper()}")))
                
                if len(image_files) > 0:
                    print(f"✓ Found {len(image_files)} image(s) in folder")
                    for img_file in image_files[:5]:  # Show first 5
                        print(f"  - {os.path.basename(img_file)}")
                    if len(image_files) > 5:
                        print(f"  ... and {len(image_files) - 5} more")
                    break
                else:
                    print(f"✗ No image files found in folder: {folder_path}")
                    print(f"  Supported formats: {', '.join(IMAGE_EXTENSIONS)}")
                    retry = input("Would you like to try again? (y/n): ").strip().lower()
                    if retry != 'y':
                        print("Exiting...")
                        sys.exit(0)
            else:
                print(f"✗ Folder not found: {folder_path}")
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Exiting...")
                    sys.exit(0)
        
        input_path = folder_path
        image_paths = sorted(image_files)
    else:
        while True:
            image_path = input("\nEnter the path to your image file: ").strip()
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
        
        input_path = image_path
        image_paths = [image_path]
    
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
    
    # Get output location
    if batch_mode:
        print("\n" + "-"*70)
        output_input = input("\nEnter output folder for HTML files (default: current folder): ").strip()
        output_folder = output_input if output_input else '.'
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        output_path = output_folder
    else:
        print("\n" + "-"*70)
        output_input = input("\nEnter output HTML filename (default: interactive_rosette_viewer.html): ").strip()
        output_file = output_input if output_input else 'interactive_rosette_viewer.html'
        
        # Ensure .html extension
        if not output_file.endswith('.html'):
            output_file += '.html'
        
        output_path = output_file
    
    return {
        'batch_mode': batch_mode,
        'input_path': input_path,
        'image_paths': image_paths,
        'output_path': output_path,
        'cell_diameter': cell_diameter,
        'min_cell_area': min_cell_area,
        'max_cell_area': max_cell_area,
        'vertex_radius': vertex_radius,
        'min_rosette_cells': min_rosette_cells
    }


def process_single_image(image_path, output_file, config):
    """
    Process a single image and generate HTML visualization.
    
    Args:
        image_path: Path to the image file
        output_file: Path for the output HTML file
        config: Dictionary with processing parameters
        
    Returns:
        Dictionary with processing results
    """
    print("\n" + "="*70)
    print(f"Processing: {os.path.basename(image_path)}")
    print("="*70)
    
    # Load images
    imgs = load_and_validate_images([image_path])
    
    if not imgs:
        print(f"ERROR: Failed to load image: {image_path}")
        return {'success': False, 'error': 'Failed to load image'}
    
    # Detect and filter cells
    mask, img, valid_cells, cell_properties = detect_cells(
        imgs, config['cell_diameter'], config['min_cell_area'], config['max_cell_area']
    )
    
    if len(valid_cells) == 0:
        print(f"WARNING: No valid cells detected in {os.path.basename(image_path)}")
        return {'success': False, 'error': 'No valid cells detected'}
    
    # Extract cell boundaries
    cell_boundaries = extract_cell_boundaries(valid_cells, cell_properties)
    
    # Find vertices where cells meet
    vertices = find_vertices(
        valid_cells, cell_boundaries, mask, config['vertex_radius'], config['min_rosette_cells']
    )
    
    count_vertices = find_vertices(
        valid_cells, cell_boundaries, mask, config['vertex_radius'], 3
    )
    
    # Cluster nearby vertices into rosettes
    rosettes = cluster_vertices(vertices, config['vertex_radius'], config['min_rosette_cells'])
    
    num_rosettes = len(rosettes)
    
    print(f"Results: {len(valid_cells)} cells, {num_rosettes} rosettes")
    
    # Generate base visualization image
    base_img_base64 = create_base_visualization(img, valid_cells, cell_properties, rosettes)
    
    # Prepare data for JavaScript
    cell_pixels, cell_data, rosette_data, cell_to_rosettes = prepare_interactive_data(
        valid_cells, cell_properties, cell_boundaries, vertices, count_vertices, rosettes
    )
    
    # Generate HTML file
    html_content = generate_html_visualization(
        base_img_base64, cell_pixels, cell_data, rosette_data, cell_to_rosettes,
        len(valid_cells), num_rosettes
    )
    
    # Save HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"✓ Created: {output_file}")
    
    return {
        'success': True,
        'num_cells': len(valid_cells),
        'num_rosettes': num_rosettes,
        'output_file': output_file
    }


def main():
    """
    Main execution function for rosette detection and visualization.
    
    Supports both single image processing and batch processing of folders.
    7. Export cell data and junction counts to CSV
    """
    # Get user input
    config = get_user_input()
    
    # Display configuration
    print("\n" + "="*70)
    print("ROSETTE DETECTION CONFIGURATION")
    print("="*70)
    if config['batch_mode']:
        print(f"Mode: Batch processing")
        print(f"Input folder: {config['input_path']}")
        print(f"Number of images: {len(config['image_paths'])}")
        print(f"Output folder: {config['output_path']}")
    else:
        print(f"Mode: Single image")
        print(f"Input image: {config['input_path']}")
        print(f"Output file: {config['output_path']}")
    
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
    
    # Find ALL vertices where cells meet (3+ cells) for comprehensive junction analysis
    all_vertices = find_vertices(
        valid_cells, cell_boundaries, mask, config['vertex_radius'], min_cells_for_vertex=3
    )
    
    # Find rosette vertices (5+ cells) for visualization
    rosette_vertices = find_vertices(
        valid_cells, cell_boundaries, mask, config['vertex_radius'], config['min_rosette_cells']
    )
  
    # Cluster nearby vertices into rosettes
    rosettes = cluster_vertices(rosette_vertices, config['vertex_radius'], config['min_rosette_cells'])
    
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

    # Calculate cell neighbors once (used for both visualization and CSV export)
    print("\nCalculating cell neighbors...")
    cell_neighbors = calculate_cell_neighbors(valid_cells, cell_boundaries)
    
    # Prepare data for JavaScript (includes all cells and their properties)
    print("Creating pixel-to-cell mapping and calculating cell properties...")
    cell_pixels, cell_data, rosette_data, cell_to_rosettes = prepare_interactive_data(
        valid_cells, cell_properties, cell_boundaries, all_vertices, rosettes, cell_neighbors
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
    print(f"Interactive visualization created: {config['output_file']}")
    print(f"Open this file in your web browser to interact with the rosettes!")
    print(f"{'='*70}")
    
    # Export data to CSV
    print("\n" + "="*70)
    print("STEP 6: EXPORTING DATA TO CSV")
    print("="*70)
    
    # Create output directory if it doesn't exist
    os.makedirs(cfg.DATA_OUTPUT_DIR, exist_ok=True)
    
    # Generate CSV filename based on image name
    image_basename = os.path.splitext(cfg.IMAGE_FILE)[0]
    csv_output_path = os.path.join(cfg.DATA_OUTPUT_DIR, f'{image_basename}_cell_data.csv')
    
    # Generate CSV export using ALL vertices (3+) for complete junction data
    generate_csv_export(mask, valid_cells, all_vertices, cell_neighbors, csv_output_path)

    print(f"\n{'='*70}")
    print(f"CSV export created: {csv_output_path}")
    print(f"{'='*70}")


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