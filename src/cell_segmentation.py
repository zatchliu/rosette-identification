class CellSegmentation:
    def __init__(self, image):
        """
        Initialize the CellSegmentation object.
        """
        self.image = image
        self.cell_images = []
        self.cell_count = 0
        self.cell_centers = []
        self.cell_areas = []

    def segment_cells(self):
        """
        Segment the cells in the image.

        Args:
            image: The image to segment the cells from.

        Returns:
            The segmented cells.
        """
        return self.cell_images

    def get_cell_count(self):
        """
        Get the number of cells in the image.

        Args:
            image: The image to get the number of cells from.

        Returns:
            The number of cells in the image.
        """
        return self.cell_count

    def get_cell_centers(self):
        """
        Get the centers of the cells in the image.

        Args:
            image: The image to get the centers of the cells from.

        Returns:
            The centers of the cells in the image.
        """
        return self.cell_centers