from src.cell_segmentation import CellSegmentation

class TestCellSegmentation:
    def test_segment_cells(self):
        """
        Test the segment_cells method.

        Returns:
            None
        """
        cell_segmentation = CellSegmentation(image)
        cell_segmentation.segment_cells()
        assert len(cell_segmentation.get_cell_images()) > 0

    def test_get_cell_count(self):
        """
        Test the get_cell_count method.

        Returns:
            None
        """
        cell_segmentation = CellSegmentation(image)
        cell_segmentation.segment_cells()
        assert cell_segmentation.get_cell_count() > 0