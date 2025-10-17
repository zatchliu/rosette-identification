from src.vertex_detection import VertexDetection


def test_set_vertex_tolerance_updates_internal_state():
    """
    Ensure the tolerance setter updates the stored pixel radius.
    """
    detector = VertexDetection()
    detector.set_vertex_tolerance(15)

    assert detector.vertex_tolerance_radius == 15


def test_detect_vertices_resets_vertex_map_and_returns_list():
    """
    Verify detect_vertices returns a list and clears any stale vertex map entries.
    """
    detector = VertexDetection()
    detector.vertex_map = {"old_vertex": ["cell_a", "cell_b"]}

    result = detector.detect_vertices(image="placeholder-image")

    assert isinstance(result, list)
    assert detector.get_vertex_map() == {}
