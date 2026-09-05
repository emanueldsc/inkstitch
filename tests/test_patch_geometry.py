from inkex import Group, PathElement

from lib.utils.patch_geometry import combined_outline, combined_outlines, create_running_path, create_satin_path, polygon_paths


def test_combined_outline_offsets_lettering_shape():
    group = Group()
    group.append(PathElement(
        d="M 0,0 L 100,0 L 100,40 L 0,40 Z",
        style="fill:none;stroke:#000000;stroke-width:10"
    ))

    outline = combined_outline(group, 2)

    assert outline is not None
    assert outline.area > 0
    assert list(polygon_paths(outline))


def test_running_path_has_inkstitch_parameters():
    path = create_running_path([(0, 0), (10, 0), (10, 10), (0, 0)], "Border", 2.5, color="#ff0000")

    assert path.get("inkstitch:stroke_method") == "running_stitch"
    assert path.get("inkstitch:max_stitch_length_mm") == "2.5"
    assert "#ff0000" in path.get("style")


def test_running_path_preserves_stabilization_stitch_length():
    path = create_running_path([(0, 0), (10, 0), (10, 10), (0, 0)], "Stabilization", 1.2)

    assert path.get("inkstitch:max_stitch_length_mm") == "1.2"


def test_combined_outlines_join_multiple_text_groups():
    first = Group()
    first.append(PathElement(d="M 0,0 L 20,0 L 20,20 L 0,20 Z", style="fill:#000000"))
    second = Group()
    second.append(PathElement(d="M 25,0 L 45,0 L 45,20 L 25,20 Z", style="fill:#000000"))

    outline = combined_outlines([first, second], 3)

    assert outline is not None
    assert len(list(polygon_paths(outline))) == 1


def test_closed_outline_can_be_converted_to_satin():
    path = create_satin_path(
        [(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)],
        "Border",
        2
    )

    assert path is not None
    assert path.get("inkstitch:satin_column") == "True"


def test_satin_method_is_preserved():
    path = create_satin_path(
        [(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)],
        "Border",
        2,
        satin_method="zigzag"
    )

    assert path is not None
    assert path.get("inkstitch:satin_method") == "zigzag"