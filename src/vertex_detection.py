"""
Vertex Detection Module

This module identifies vertices where multiple cells meet at common points.
It samples candidate locations and determines which points have enough nearby
cell boundaries to qualify as vertices.
"""

import numpy as np


def find_vertices(valid_cells, cell_boundaries, mask, vertex_radius, min_cells):
    """
    Identify vertices where multiple cells meet at a common point.
    
    This function samples points in the image and checks how many cell boundaries
    are within vertex_radius of each point. Points where min_cells or more cells
    meet are considered vertices.
    
    Args:
        valid_cells: List of valid cell IDs
        cell_boundaries: Dictionary mapping cell_id to boundary coordinates
        mask: Segmentation mask array
        vertex_radius: Search radius for nearby cells (pixels)
        min_cells: Minimum cells required to form a vertex
        
    Returns:
        List of vertex dictionaries containing location, cells, and num_cells
    """
    print("\n" + "="*70)
    print("STEP 3: IDENTIFYING VERTICES WHERE CELLS MEET")
    print("="*70)
    
    vertices = []
    
    # Create a grid of candidate vertex points
    y_coords, x_coords = np.where(mask > 0)
    sample_points = np.column_stack([y_coords, x_coords])
    
    # Sample every Nth point to speed up computation
    sample_stride = max(1, len(sample_points) // 10000) 
    sample_points = sample_points[::sample_stride]
    
    print(f"Searching {len(sample_points)} candidate vertex locations...")
    
    # Check each candidate point
    for point in sample_points:
        y, x = point
        
        # Find all cells within vertex_radius of this point
        cells_near_point = []
        
        for cell_id in valid_cells:
            boundaries = cell_boundaries[cell_id]
            
            # Calculate minimum distance from point to cell boundary
            distances = np.sqrt(np.sum((boundaries - point)**2, axis=1))
            min_dist = np.min(distances)
            
            if min_dist <= vertex_radius:
                cells_near_point.append(cell_id)
        
        # If enough cells meet here, record as vertex
        if len(cells_near_point) >= min_cells:
            vertices.append({
                'location': (x, y),
                'cells': cells_near_point,
                'num_cells': len(cells_near_point)
            })
    
    print(f"Found {len(vertices)} candidate vertices")
    
    return vertices