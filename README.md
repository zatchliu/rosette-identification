# Rosette Identification
### **We are using 2 grace days for milestone 3**

This is a project for COMP 333 in collaboration with the Mitchel lab. 

## Team Members
- **braeden-falzarano**: Braeden Falzarano
- **zatchliu**: Zachary Liu
- **therevboss**: Oliver Wyner

## [Style Guide](/StyleGuide.md)

---

## What This Project Does

This toolkit automatically detects and identifies **rosettes** in microscopy images of cells. 

**What is a rosette?** A rosette is a cluster of 5 or more cells that meet at a central point (called a vertex), arranged in a radial pattern like the petals of a flower.

**What the program does:**
1. Takes a microscopy image as input
2. Identifies individual cells in the image
3. Finds points where multiple cells meet (vertices)
4. Identifies rosettes (where 5+ cells meet at a vertex)
5. Creates an interactive visualization where you can hover over cells to highlight rosettes

**Output:** An HTML file that you open in your web browser to explore the detected rosettes interactively.

---

## System Requirements

### All Users Need:
- **Python 3.10 or 3.11** installed on your computer
  - To check if you have Python: Open Terminal (Mac) or Command Prompt (Windows) and type `python --version`
  - If you don't have Python, download it from [python.org]([https://www.python.org/downloads/](https://www.python.org/downloads/release/python-3110/))

### GPU Support (for faster processing):
- **macOS with M1/M2/M3 chip**: GPU support is available automatically
- **Windows**: CPU-only mode (GPU not currently supported by CellPose on Windows)

**Note:** GPU makes processing faster, but CPU mode still works - it just takes longer.

---

## Installation Guide

**Important:** We will create a "virtual environment" to keep this project's software separate from other Python projects on your computer. This prevents conflicts between different versions of software.

### For macOS Users (M1/M2/M3 chips)

#### Step 1: Open Terminal
- Press `Command + Space` to open Spotlight
- Type "Terminal" and press Enter

#### Step 2: Navigate to Where You Want the Project

Instead of typing folder paths, let's copy the path from Finder:

1. Open **Finder**
2. Navigate to where you want to put the project (Documents, Desktop, etc.)
3. Right-click (or Control + Click) on the folder
4. Hold down the **Option** key (you'll see "Copy" change to "Copy as Pathname")
5. Click **Copy as Pathname**
6. Go back to Terminal and type `cd ` (with a space after cd)
7. Press `Command + V` to paste the path
8. Press Enter

**Example:** If you copied your Documents folder, you'll see something like this before you press enter:
```bash
cd /Users/yourname/Documents
```
and something like this after you hit enter: 
```bash
braedenfalzarano@Braedens-MacBook-Pro-7 Documents % 
```
**Note:** It won't say exactly "braedenfalzarano@Braedens-MacBook-Pro-7", but it should say something identifying your machine. This is not important or relevant to the previous commands that you ran and should stay the same throughout your use of the terminal.

#### Step 3: Clone (Download) This Project

**Note:** You'll need a GitHub account to clone this repository. If you don't have one, you can create a free account at [github.com](https://github.com).

```bash
git clone https://github.com/YOUR-USERNAME/rosette-identification.git
cd rosette-identification
```

**Note:** YOUR-USERNAME is your GitHub username

**Additional Resources:**
- [Installing and setting up GitHub](https://docs.github.com/en/get-started/git-basics/set-up-git)
- [Cloning a Repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

#### Step 4: Create a Virtual Environment
A virtual environment is like a separate workspace for this project.

```bash
python3.11 -m venv rosette
```

This creates a virtual environment called `rosette` that contains all the software this project needs.

#### Step 5: Activate the Virtual Environment
```bash
source rosette/bin/activate
```

You'll see `(rosette)` appear at the start of your command line. This means you're "inside" the virtual environment.

#### Step 6: Install Required Software

```bash
# Check your Python version
python --version
# If it prints "Python 3.11.SOME_NUMBER," you are all set and ready to proceed
# If not, you may need to check your Python install

# Upgrade pip
pip install --upgrade pip

# Install opencv first
python -m pip install -U pip wheel setuptools
python -m pip install --only-binary=:all: "opencv-python-headless==4.10.0.84"

# Install PyTorch
pip install torch torchvision

# Install CellPose with GPU support
pip install 'cellpose[gui]'

# Install other required packages
pip install numpy==1.24.3 scipy==1.11.4 matplotlib==3.8.2 Pillow==10.1.0
```

This may take a few minutes to download and install everything. If it proceeds without any red error messages, you should be all set to go.

#### Step 7: Check for GPU Compatibility
```bash
python -c "from cellpose import core; print(f'GPU available: {core.use_gpu()}')"
```

If you see: `GPU available: True`, your system can use GPUs to increase processing speed.
If not, the code will still run, but may take longer due to using CPUs rather than GPUs.

**Installation complete!** You can now skip to **Running the Rosette Detection**.

---

### For Windows Users

#### Step 1: Open Command Prompt
- Press `Windows Key + R`
- Type `cmd` and press Enter

#### Step 2: Navigate to Where You Want the Project
```cmd
# Go to your Documents folder
cd %USERPROFILE%\Documents

# Or go to your Desktop
cd %USERPROFILE%\Desktop
```

#### Step 3: Clone (Download) This Project
```cmd
git clone https://github.com/YOUR-USERNAME/rosette-identification.git
cd rosette-identification
```

**Note:** YOUR-USERNAME is your GitHub username


#### Step 4: Create a Virtual Environment using miniconda
Link to miniconda installation instructions [here](https://www.anaconda.com/docs/getting-started/miniconda/install)

```cmd
conda create -n rosette python=3.10 -y
```

#### Step 5: Activate the Virtual Environment
```cmd
conda activate rosette
```

You'll see `(rosette)` appear at the start of your command line.

#### Step 6: Install Required Software

**Note:** Windows can only use CPU mode (not GPU) for CellPose currently.

```cmd
python -m pip install -U pip wheel setuptools
python -m pip install --only-binary=:all: "opencv-python-headless==4.10.0.84"

# Install pyTorch for CPU use
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install CellPose
pip install "cellpose[gui]"

# Install other packages
pip install numpy==1.24.3 scipy==1.11.4 matplotlib==3.8.2 Pillow==10.1.0
```

This may take a few minutes to download and install everything.

#### Step 7: Verify Installation
```cmd
python -c "from cellpose import core; print(f'GPU available: {core.use_gpu()}')"
```

You will likely see: `GPU available: False`

This is normal for Windows - it will use CPU mode as stated earlier.

**Installation complete!** Continue to the next section.

---

## Running the Rosette Detection

### Step 1: Make Sure Your Virtual Environment is Active

You should see `(rosette)` at the start of your command line. If not:

**Mac:**
```bash
source rosette/bin/activate
```

**Windows:**
```cmd
rosette\Scripts\activate
```

### Step 2: Run the Detection

**Mac:**
```bash
# To avoid MPS Fallback error (this is necessary on macOS)
export PYTORCH_ENABLE_MPS_FALLBACK=1

python app.py
```

**Windows:**
```cmd
# To avoid MPS Fallback error (just to be safe on Windows)
export PYTORCH_ENABLE_MPS_FALLBACK=1

python app.py
```

### Step 3: Wait for Processing

You'll see progress messages like:
```
==================================================================
STEP 1: DETECTING INDIVIDUAL CELLS
==================================================================
Total objects detected: 1406
Valid cells (after size filtering): 1354

==================================================================
STEP 2: FINDING CELL BOUNDARIES AND CONTACT POINTS
==================================================================
...
```

**Processing time:**
- Small images (< 1000 cells): ~4 minutes
- Large images (> 1000 cells): 5-10 minutes
- Mac with GPU: Faster
- Windows with CPU: Slower (but it works!)

### Step 4: Open the Output

When processing completes, you'll see:
```
Interactive visualization created: interactive_rosette_viewer.html
Open this file in your web browser to interact with the rosettes!
```

1. Look in the `rosette-identification` folder
2. Find the file `interactive_rosette_viewer.html`
3. Double-click to open it in your web browser (Chrome, Firefox, Safari, Edge, etc)

---

## Understanding the Output

### The Interactive Visualization

When you open `interactive_rosette_viewer.html`, you'll see:

**Top of page:**
- **Total Cells**: Number of individual cells detected
- **Total Rosettes**: Number of rosettes found
- **Cells in Rosettes**: How many cells are part of rosettes

**The Image:**
- **Cyan outlines**: All cell boundaries
- **Green cells**: Cells that are part of rosettes
- **Red Dots**: Centers of rosettes (vertices)

**Interactive Feature:**
- **Hover your mouse** over any green cell
- That cell's rosette will highlight in **orange**
- The rosette center will get bigger and show a label (R1, R2, etc.)
- Information box shows which cell and rosette you're looking at

### Understanding the Console Output

When the program runs, it also prints detailed information:

```
Total cells detected: 1354
Total rosettes found: 155

Rosette Details:
#     Center (x,y)         Num Cells    Cell IDs                      
1     (559, 25)            5            [38, 39, 81, 85, 62]
2     (917, 29)            5            [67, 99, 73, 9, 44]
...
```

- **Center (x,y)**: Pixel coordinates of the rosette center
- **Num Cells**: How many cells in that rosette
- **Cell IDs**: Which cells belong to that rosette

---

## Adjusting Detection Parameters

If the detection isn't working well (finding too many or too few rosettes), you can adjust the settings.

**Note:** We understand that the parameters are not tuned perfectly at the moment. This is something we plan to tweak as we move forward.

### Where to Adjust Settings

Open `config.py` in a text editor. You'll see:

```python
# DETECTION PARAMETERS
CELL_DIAMETER = 30              # Estimated cell diameter for CellPose detection (pixels)
MIN_CELL_AREA = 100             # Minimum area to count as valid cell (pixels)
MAX_CELL_AREA = 5000            # Maximum area to count as valid cell (pixels)
VERTEX_RADIUS = 15              # Search radius for cells meeting at a vertex (pixels)
MIN_CELLS_FOR_ROSETTE = 5       # Minimum cells required to form a rosette
```

### What Each Parameter Does

**CELL_DIAMETER** (default: 30)
- How big is a typical cell in your image (in pixels)?
- **Too small** → Might break one cell into multiple pieces
- **Too large** → Might merge multiple cells together
- **How to measure**: Open your image, zoom in, and count pixels across a typical cell

**MIN_CELL_AREA** (default: 100)
- Minimum size to count as a real cell
- **Too small** → Detects noise as cells
- **Too large** → Misses small cells
- Helps filter out debris and artifacts

**MAX_CELL_AREA** (default: 5000)
- Maximum size to count as a single cell
- **Too large** → Might count cell clumps as one cell
- **Too small** → Rejects large cells
- Helps filter out artifacts

**VERTEX_RADIUS** (default: 15)
- How close do cell boundaries need to be to "meet at a point"?
- **Too small** → Misses rosettes where cells don't touch perfectly
- **Too large** → Incorrectly groups distant cells as rosettes
- **Good starting point**: 0.5 to 1.0 times the cell diameter

**MIN_CELLS_FOR_ROSETTE** (default: 5)
- Minimum cells needed to form a rosette
- By definition, a rosette has 5+ cells
- You probably don't want to change this

### Example Adjustments

**If you're getting too many false rosettes:**
```python
VERTEX_RADIUS = 10              # Make stricter - cells must be closer
MIN_CELL_AREA = 200             # Ignore smaller debris
```

**If you're missing real rosettes:**
```python
VERTEX_RADIUS = 20              # More lenient - cells can be farther apart
CELL_DIAMETER = 35              # If your cells are larger
```

**After changing settings**, run the program again:
```bash
python app.py
```

---

## Testing Individual Components

You can test each step of the detection process separately to diagnose issues.

### Test 1: Cell Segmentation Only

This shows just the cell detection, without rosette finding.

```bash
python tests/test_cell_segmentation.py
```

**Output:** `output/visualizations/test_cell_segmentation_results.png`

**What to look for:**
- Are all cells outlined in cyan?
- Are cells broken into pieces? (CELL_DIAMETER too small)
- Are multiple cells merged? (CELL_DIAMETER too large)
- Is debris detected as cells? (MIN_CELL_AREA too small)

### Test 2: Vertex Detection

This shows all points where 3+ cells meet.

```bash
python tests/test_vertex_detection.py
```

**Output:** `output/visualizations/test_vertex_detection_results.png`

**What to look for:**
- Red dots should appear where cells touch
- Too many dots? (VERTEX_RADIUS too large)
- Missing obvious junctions? (VERTEX_RADIUS too small)

### Test 3: Complete Rosette Detection

This is the full pipeline with visualization.

```bash
python tests/test_rosette_detection.py
```

**Output:** `output/visualizations/test_rosette_detection_results.png`

**What to look for:**
- Green cells are in rosettes
- Red stars mark rosette centers
- Red circle marks VERTEX_RADIUS
- Compare to what you expect to see

---

## Troubleshooting

### Problem: "Command not found: python"

**Solution:**
- Try `python3` instead of `python`
- Make sure Python is installed: Visit [python.org](https://www.python.org/downloads/)

### Problem: "ModuleNotFoundError: No module named 'cellpose'"

**Solution:**
- Make sure your virtual environment is activated (you should see `(rosette)` in your terminal)
- Run the pip install commands again

### Problem: "zsh: no matches found: cellpose[gui]" (Mac only)

**Solution:**
- Use quotes around the command:
```bash
pip install 'cellpose[gui]'
```

### Problem: Processing is very slow

**Solutions:**
- **If on Mac**: Check that GPU is enabled. Run:
  ```bash
  python -c "from cellpose import core; print(f'GPU available: {core.use_gpu()}')"
  ```
  Should say `True`. If `False`, reinstall cellpose.

- **If on Windows**: This is normal - CPU mode is slower. Be patient, it will complete.

- **For both**: Try processing a smaller region of your image first to test settings

### Problem: Too many/too few rosettes detected

**Solution:**
- See the **Adjusting Detection Parameters** section
- Most common fix: Adjust `VERTEX_RADIUS`
- Start with testing just cell segmentation to make sure cells are detected correctly


---

## Additional Resources

- **CellPose Documentation**: [cellpose.readthedocs.io](https://cellpose.readthedocs.io/)
- **Python Virtual Environments**: [docs.python.org/3/tutorial/venv.html](https://docs.python.org/3/tutorial/venv.html)
- **Project Issues**: If you find bugs, report them on our GitHub Issues page

---

## For Developers

See [StyleGuide.md](StyleGuide.md) for code contribution guidelines.

### Project Structure
```
rosette-identification/             # root of the directory
├── app.py                          # Main application entry point
├── config.py                       # Configuration parameters
├── src/
│   ├── cell_segmentation.py        # Cell detection module
│   ├── vertex_detection.py         # Vertex identification module
│   └── rosette_detection.py        # Rosette clustering and visualization
├── tests/
│   ├── test_cell_segmentation.py   # Test cell detection
│   ├── test_vertex_detection.py    # Test vertex detection
│   └── test_rosette_detection.py   # Test complete pipeline
├── data/                           # Input images go here
└── output/                         # Generated outputs
    ├── visualizations/             # Static image outputs
    └── data/                       # Text data outputs
```
