"""
Rosette Detection Module

This module takes all vertices (from vertex_detection) and identifies rosettes
by filtering for vertices where 5+ cells meet, then clustering nearby vertices
that likely represent the same rosette. It also creates interactive visualizations.
"""

import numpy as np
import json
import base64
from io import BytesIO
from collections import defaultdict
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation


def filter_rosette_vertices(vertices, min_cells_for_rosette=5):
    """
    Filter vertices to only include those with enough cells to be rosettes.
    
    Args:
        vertices: List of all vertex dictionaries
        min_cells_for_rosette: Minimum cells required for a rosette (default: 5)
        
    Returns:
        List of vertex dictionaries that qualify as potential rosettes
    """
    rosette_vertices = [v for v in vertices if v['num_cells'] >= min_cells_for_rosette]
    print(f"Filtered {len(rosette_vertices)} rosette candidates (5+ cells) from {len(vertices)} total vertices")
    return rosette_vertices


def cluster_vertices(vertices, vertex_radius, min_cells_for_rosette=5):
    """
    Filter for rosette vertices and merge nearby ones that likely represent the same rosette.
    
    First filters vertices to only those with min_cells_for_rosette or more cells.
    Then, vertices within 1.5 * vertex_radius of each other are merged by averaging
    their locations and combining their cell lists.
    
    Args:
        vertices: List of ALL vertex dictionaries (including small junctions)
        vertex_radius: Radius used for vertex detection (pixels)
        min_cells_for_rosette: Minimum cells required for a rosette (default: 5)
        
    Returns:
        List of merged rosette dictionaries
    """
    print("\n" + "="*70)
    print("STEP 4: FILTERING AND CLUSTERING ROSETTE VERTICES")
    print("="*70)
    
    # First, filter for rosette vertices only (5+ cells)
    rosette_vertices = filter_rosette_vertices(vertices, min_cells_for_rosette)
    
    if len(rosette_vertices) == 0:
        print("No rosettes found (no vertices with 5+ cells)")
        return []
    
    vertex_locations = np.array([v['location'] for v in rosette_vertices])
    
    # Use distance-based clustering to merge nearby vertices
    merge_distance = vertex_radius * 1.5
    merged_vertices = []
    used = set()
    
    for i, vertex in enumerate(rosette_vertices):
        if i in used:
            continue
        
        # Find all vertices within merge_distance
        loc = vertex_locations[i]
        distances = np.sqrt(np.sum((vertex_locations - loc)**2, axis=1))
        nearby_indices = np.where(distances <= merge_distance)[0]
        
        # Merge all nearby vertices
        merged_cells = set()
        merged_locations = []
        for idx in nearby_indices:
            merged_cells.update(rosette_vertices[idx]['cells'])
            merged_locations.append(vertex_locations[idx])
            used.add(idx)
        
        # Calculate average location
        avg_location = np.mean(merged_locations, axis=0)
        
        merged_vertices.append({
            'location': tuple(avg_location.astype(int)),
            'cells': list(merged_cells),
            'num_cells': len(merged_cells)
        })
    
    print(f"Identified {len(merged_vertices)} rosettes after merging nearby vertices")
    
    return merged_vertices


def calculate_perimeter(cell_mask):
    """
    Calculate the perimeter of a cell by counting boundary pixels.
    
    Args:
        cell_mask: Binary mask of the cell
        
    Returns:
        Perimeter in pixels
    """
    from scipy.ndimage import binary_erosion
    eroded = binary_erosion(cell_mask)
    boundary = cell_mask & ~eroded
    perimeter = np.sum(boundary)
    return perimeter


def calculate_cell_neighbors(valid_cells, cell_boundaries):
    """
    Calculate the number of neighboring cells for each cell.
    Two cells are neighbors if their boundaries are within 2 pixels of each other.
    
    Args:
        valid_cells: List of valid cell IDs
        cell_boundaries: Dictionary mapping cell_id to boundary coordinates
        
    Returns:
        Dictionary mapping cell_id to number of neighbors
    """
    print("Calculating cell neighbors...")
    cell_neighbors = {}
    
    for cell_id in valid_cells:
        neighbors = set()
        boundary = cell_boundaries[cell_id]
        
        for other_id in valid_cells:
            if other_id == cell_id:
                continue
            
            other_boundary = cell_boundaries[other_id]
            
            # Calculate minimum distance between boundaries
            for point in boundary:
                distances = np.sqrt(np.sum((other_boundary - point)**2, axis=1))
                if np.min(distances) <= 2:  # Adjacent if within 2 pixels
                    neighbors.add(other_id)
                    break
        
        cell_neighbors[cell_id] = len(neighbors)
    
    return cell_neighbors


def calculate_cell_vertices(valid_cells, vertices):
    """
    Calculate the number of vertices each cell participates in.
    
    Args:
        valid_cells: List of valid cell IDs
        vertices: List of all vertex dictionaries
        
    Returns:
        Dictionary mapping cell_id to number of vertices
    """
    print("Calculating cell vertices...")
    cell_vertex_count = defaultdict(int)
    
    for vertex in vertices:
        for cell_id in vertex['cells']:
            cell_vertex_count[cell_id] += 1
    
    
    return dict(cell_vertex_count)


def create_base_visualization(img, valid_cells, cell_properties, rosettes):
    """
    Create base image with cell outlines and rosettes highlighted in green.
    Red dots are NOT drawn here - they will be drawn dynamically in JavaScript.
    
    Uses PIL to ensure exact pixel-coordinate correspondence between the base
    image and the JavaScript canvas overlay.
    
    Args:
        img: Original image array
        valid_cells: List of valid cell IDs
        cell_properties: Dictionary with cell properties
        rosettes: List of rosette dictionaries
        
    Returns:
        Base64-encoded PNG string of the visualization
    """
    # Normalize image to 0-255 range
    if len(img.shape) == 3:
        base_img = img
    else:
        base_img = np.stack([img, img, img], axis=-1)
    
    if base_img.max() > 1:
        base_img_normalized = (base_img.astype(float) / base_img.max() * 255).astype(np.uint8)
    else:
        base_img_normalized = (base_img * 255).astype(np.uint8)
    
    # Convert to PIL Image
    base_pil = Image.fromarray(base_img_normalized)
    
    # Create transparent overlay layer
    overlay = Image.new('RGBA', base_pil.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Draw all cell outlines in cyan
    outline_color = (0, 255, 255, 180)  # Cyan with transparency
    
    for cell_id in valid_cells:
        cell_mask = cell_properties[cell_id]['mask']
        
        # Get outline by dilation
        dilated = binary_dilation(cell_mask, iterations=1)
        outline = dilated & ~cell_mask
        ys, xs = np.where(outline)
        
        # Draw outline pixels
        for y, x in zip(ys, xs):
            overlay.putpixel((x, y), outline_color)
    
    # Highlight all rosette cells in green
    green_color = (0, 255, 0, 76)  # Green with 30% opacity
    
    for rosette in rosettes:
        for cell_id in rosette['cells']:
            cell_mask = cell_properties[cell_id]['mask']
            ys, xs = np.where(cell_mask)
            
            # Draw filled pixels
            for y, x in zip(ys, xs):
                overlay.putpixel((x, y), green_color)
    
    # Composite overlay onto base image
    base_pil = base_pil.convert('RGBA')
    final_img = Image.alpha_composite(base_pil, overlay)
    
    # RED DOTS ARE NOW DRAWN IN JAVASCRIPT, NOT HERE
    
    # Convert to base64 for HTML embedding
    buf = BytesIO()
    final_img.save(buf, format='PNG')
    buf.seek(0)
    base_img_base64 = base64.b64encode(buf.read()).decode()
    
    return base_img_base64


def prepare_interactive_data(valid_cells, cell_properties, cell_boundaries, vertices, rosettes):
    """
    Prepare data structures for JavaScript interactive visualization.
    
    Args:
        valid_cells: List of valid cell IDs
        cell_properties: Dictionary with cell properties
        cell_boundaries: Dictionary mapping cell_id to boundary coordinates
        vertices: List of all vertex dictionaries
        rosettes: List of rosette dictionaries
        
    Returns:
        Tuple of (cell_pixels, cell_data, rosette_data, cell_to_rosettes)
    """
    # Calculate additional cell properties
    cell_neighbors = calculate_cell_neighbors(valid_cells, cell_boundaries)
    cell_vertex_count = calculate_cell_vertices(valid_cells, vertices)
    
    # Build cell-to-rosettes mapping
    cell_to_rosettes = defaultdict(list)
    for rosette_idx, rosette in enumerate(rosettes):
        for cell_id in rosette['cells']:
            cell_to_rosettes[cell_id].append(rosette_idx)
    
    # Prepare pixel data for ALL cells
    cell_pixels = {}
    for cell_id in valid_cells:
        ys, xs = np.where(cell_properties[cell_id]['mask'])
        cell_pixels[int(cell_id)] = [[int(y), int(x)] for y, x in zip(ys, xs)]
    
    # Prepare comprehensive cell data
    cell_data = {}
    for cell_id in valid_cells:
        cell_mask = cell_properties[cell_id]['mask']
        area = cell_properties[cell_id]['area']
        perimeter = calculate_perimeter(cell_mask)
        num_neighbors = cell_neighbors.get(cell_id, 0)
        num_vertices = cell_vertex_count.get(cell_id, 0)
        
        cell_data[int(cell_id)] = {
            'area': int(area),
            'perimeter': int(perimeter),
            'num_neighbors': int(num_neighbors),
            'num_vertices': int(num_vertices),
            'in_rosette': cell_id in cell_to_rosettes
        }
    
    # Prepare rosette data
    rosette_data = []
    for idx, rosette in enumerate(rosettes):
        rosette_data.append({
            'id': idx,
            'cells': [int(c) for c in rosette['cells']],
            'center': [int(rosette['location'][0]), int(rosette['location'][1])],
            'num_cells': rosette['num_cells']
        })
    
    return cell_pixels, cell_data, rosette_data, cell_to_rosettes


def generate_html_visualization(base_img_base64, cell_pixels, cell_data, rosette_data, 
                                cell_to_rosettes, num_cells, num_rosettes):
    """
    Generate interactive HTML visualization file.
    
    Creates an HTML file with embedded JavaScript that allows users to hover
    over cells and see their properties and associated rosettes. Red dots are
    drawn dynamically and can be removed by clicking.
    
    Args:
        base_img_base64: Base64-encoded PNG string of base visualization
        cell_pixels: Dictionary mapping cell_id to pixel coordinates
        cell_data: Dictionary mapping cell_id to cell properties
        rosette_data: List of rosette information dictionaries
        cell_to_rosettes: Dictionary mapping cell_id to rosette indices
        num_cells: Total number of valid cells detected
        num_rosettes: Total number of rosettes identified
        
    Returns:
        String containing complete HTML document
    """
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Rosette Visualization</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #1a1a1a;
            color: #ffffff;
        }}
        #container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #4CAF50;
        }}
        #info {{
            background-color: #2a2a2a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        #canvas-container {{
            position: relative;
            display: inline-block;
            margin: 0 auto;
            display: block;
        }}
        canvas {{
            border: 2px solid #4CAF50;
            cursor: crosshair;
            display: block;
        }}
        #stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
        }}
        .stat {{
            background-color: #333;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            font-size: 12px;
            color: #aaa;
        }}
        #hover-info {{
            background-color: #444;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            min-height: 80px;
        }}
        .cell-property {{
            display: inline-block;
            margin-right: 15px;
            margin-top: 5px;
        }}
        .property-label {{
            color: #aaa;
            font-size: 12px;
        }}
        .property-value {{
            color: #4CAF50;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div id="container">
        <h1>Interactive Rosette Visualization</h1>
        <div id="info">
            <div id="stats">
                <div class="stat">
                    <div class="stat-value">{num_cells}</div>
                    <div class="stat-label">Total Cells</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="rosette-count">{num_rosettes}</div>
                    <div class="stat-label">Total Rosettes</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len([c for c in cell_data.values() if c['in_rosette']])}</div>
                    <div class="stat-label">Cells in Rosettes</div>
                </div>
            </div>
            <div id="hover-info">
                <strong>Instructions:</strong> Hover over any cell to see its properties. 
                Rosette cells are shown in green. Click on a red dot to remove that rosette.
            </div>
        </div>
        
        <div id="canvas-container">
            <canvas id="canvas"></canvas>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Data from Python
        const cellPixels = {json.dumps(cell_pixels)};
        const cellData = {json.dumps(cell_data)};
        const rosettes = {json.dumps(rosette_data)};
        const cellToRosettes = {json.dumps({int(k): v for k, v in cell_to_rosettes.items()})};
        
        // Load base image
        const baseImg = new Image();
        baseImg.src = 'data:image/png;base64,{base_img_base64}';
        
        let currentHighlightedRosettes = new Set();
        let pixelToCellMap = new Map();
        let removedRosettes = new Set(); // Track removed rosettes
        
        baseImg.onload = function() {{
            // Set canvas internal dimensions to match image exactly
            canvas.width = baseImg.width;
            canvas.height = baseImg.height;
            
            // Set canvas CSS display size to match internal dimensions
            canvas.style.width = baseImg.width + 'px';
            canvas.style.height = baseImg.height + 'px';
            
            // Build reverse lookup: pixel -> cell_id
            console.log('Building pixel-to-cell map...');
            for (const [cellId, pixels] of Object.entries(cellPixels)) {{
                for (const [y, x] of pixels) {{
                    const key = `${{x}},${{y}}`;
                    pixelToCellMap.set(key, parseInt(cellId));
                }}
            }}
            console.log(`Mapped ${{pixelToCellMap.size}} pixels`);
            
            // Initial draw
            drawImage();
        }};
        
        function drawImage() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(baseImg, 0, 0);
            
            // Draw gray mask over removed rosettes to hide the green
            if (removedRosettes.size > 0) {{
                ctx.fillStyle = 'rgba(26, 26, 26, 0.85)';  // Dark gray mask matching background
                
                removedRosettes.forEach(rosetteIdx => {{
                    const rosette = rosettes[rosetteIdx];
                    rosette.cells.forEach(cellId => {{
                        const pixels = cellPixels[cellId];
                        if (pixels) {{
                            pixels.forEach(([y, x]) => {{
                                ctx.fillRect(x, y, 1, 1);
                            }});
                        }}
                    }});
                }});
            }}
            
            // Draw red dots for active rosettes (not removed)
            rosettes.forEach((rosette, rosetteIdx) => {{
                if (removedRosettes.has(rosetteIdx)) return;
                
                const [cx, cy] = rosette.center;
                const radius = 6;
                
                ctx.fillStyle = 'rgba(255, 0, 0, 1)';
                ctx.beginPath();
                ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
                ctx.fill();
                
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 1;
                ctx.stroke();
            }});
            
            // Draw highlighted rosettes in ORANGE (on hover)
            if (currentHighlightedRosettes.size > 0) {{
                ctx.fillStyle = 'rgba(255, 140, 0, 0.5)';
                
                currentHighlightedRosettes.forEach(rosetteIdx => {{
                    if (removedRosettes.has(rosetteIdx)) return;
                    
                    const rosette = rosettes[rosetteIdx];
                    rosette.cells.forEach(cellId => {{
                        const pixels = cellPixels[cellId];
                        if (pixels) {{
                            pixels.forEach(([y, x]) => {{
                                ctx.fillRect(x, y, 1, 1);
                            }});
                        }}
                    }});
                    
                    // Draw emphasized center marker for hovered rosette
                    const [cx, cy] = rosette.center;
                    
                    ctx.fillStyle = 'rgba(255, 0, 0, 1)';
                    ctx.beginPath();
                    ctx.arc(cx, cy, 10, 0, 2 * Math.PI);
                    ctx.fill();
                    
                    ctx.strokeStyle = 'white';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                    ctx.fillRect(cx + 12, cy - 16, 50, 20);
                    
                    ctx.fillStyle = 'white';
                    ctx.font = 'bold 14px Arial';
                    ctx.fillText(`R${{rosetteIdx + 1}}`, cx + 16, cy);
                    
                    ctx.fillStyle = 'rgba(255, 140, 0, 0.5)';
                }});
            }}
        }}
        
        // Handle mouse movement for interactive highlighting
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const x = Math.floor(e.clientX - rect.left);
            const y = Math.floor(e.clientY - rect.top);
            
            const key = `${{x}},${{y}}`;
            const cellId = pixelToCellMap.get(key);
            
            if (cellId && cellData[cellId]) {{
                const data = cellData[cellId];
                const rosetteIndices = cellToRosettes[cellId] || [];
                
                // Filter out removed rosettes
                const activeRosetteIndices = rosetteIndices.filter(idx => !removedRosettes.has(idx));
                const newSet = new Set(activeRosetteIndices);
                
                // Update highlighting if changed
                if (![...newSet].every(r => currentHighlightedRosettes.has(r)) ||
                    ![...currentHighlightedRosettes].every(r => newSet.has(r))) {{
                    currentHighlightedRosettes = newSet;
                    drawImage();
                }}
                
                // Build info display
                let infoHTML = `<strong>Cell ID:</strong> ${{cellId}}<br>`;
                infoHTML += `<div style="margin-top: 8px;">`;
                infoHTML += `<div class="cell-property"><span class="property-label">Area:</span> <span class="property-value">${{data.area}} px²</span></div>`;
                infoHTML += `<div class="cell-property"><span class="property-label">Perimeter:</span> <span class="property-value">${{data.perimeter}} px</span></div>`;
                infoHTML += `<div class="cell-property"><span class="property-label">Neighbors:</span> <span class="property-value">${{data.num_neighbors}}</span></div>`;
                infoHTML += `<div class="cell-property"><span class="property-label">Vertices:</span> <span class="property-value">${{data.num_vertices}}</span></div>`;
                infoHTML += `</div>`;
                
                if (activeRosetteIndices.length > 0) {{
                    const rosetteInfo = activeRosetteIndices.map(idx => {{
                        const r = rosettes[idx];
                        return `Rosette #${{idx + 1}} (${{r.num_cells}} cells)`;
                    }}).join(', ');
                    infoHTML += `<div style="margin-top: 8px;"><strong>Part of:</strong> ${{rosetteInfo}}</div>`;
                    infoHTML += `<div style="margin-top: 5px; color: #aaa; font-size: 12px;">(Click on red dot to remove rosette)</div>`;
                }}
                
                document.getElementById('hover-info').innerHTML = infoHTML;
            }} else {{
                if (currentHighlightedRosettes.size > 0) {{
                    currentHighlightedRosettes = new Set();
                    drawImage();
                }}
                document.getElementById('hover-info').innerHTML = 
                    '<strong>Instructions:</strong> Hover over any cell to see its properties. Rosette cells are shown in green. Click on a red dot to remove that rosette.';
            }}
        }});
        
        // Clear highlighting when mouse leaves canvas
        canvas.addEventListener('mouseleave', () => {{
            currentHighlightedRosettes = new Set();
            drawImage();
            document.getElementById('hover-info').innerHTML = 
                '<strong>Instructions:</strong> Hover over any cell to see its properties. Rosette cells are shown in green. Click on a red dot to remove that rosette.';
        }});
        
        // Handle click to remove rosettes (click on red dot)
        canvas.addEventListener('click', (e) => {{
            const rect = canvas.getBoundingClientRect();
            const x = Math.floor(e.clientX - rect.left);
            const y = Math.floor(e.clientY - rect.top);
            
            // Check if click is on any rosette center (red dot)
            for (let i = 0; i < rosettes.length; i++) {{
                if (removedRosettes.has(i)) continue;
                
                const [cx, cy] = rosettes[i].center;
                const distance = Math.sqrt((x - cx) ** 2 + (y - cy) ** 2);
                
                // If clicked within the red dot (radius 6, but give some leeway)
                if (distance <= 10) {{
                    removedRosettes.add(i);
                    currentHighlightedRosettes.delete(i);
                    drawImage();
                    
                    // Update rosette count
                    const numRemaining = rosettes.length - removedRosettes.size;
                    document.getElementById('rosette-count').textContent = numRemaining;
                    
                    document.getElementById('hover-info').innerHTML = 
                        `<strong>Rosette #${{i + 1}} removed!</strong> ${{numRemaining}} rosette(s) remaining.`;
                    return;
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html_content