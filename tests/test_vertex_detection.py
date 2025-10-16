from src.vertex_detection import VertexDetection


def test_set_vertex_tolerance_updates_threshold():
    """
    Ensure the vertex tolerance setter updates the internal threshold.
    """
    detector = VertexDetection(vertex_tolerance=5)
    detector.set_vertex_tolerance(12)

    assert detector.vertex_tolerance == 12


def test_detect_vertices_uses_segmentation_and_updates_map():
    """
    Verify detect_vertices calls the segmentation service and resets vertex_map.
    """

    class DummySegmentation:
        def __init__(self):
            self.called_with = None

        def segment_cells(self, image):
            self.called_with = image
            return {"cells": [1, 2], "vertices": [{"id": "v1"}]}

    dummy_segmentation = DummySegmentation()
    detector = VertexDetection(segmentation_service=dummy_segmentation)
    result = detector.detect_vertices(image="dummy-image")

    assert dummy_segmentation.called_with == "dummy-image"
    assert detector.get_vertex_map() == {}
    assert result == []
