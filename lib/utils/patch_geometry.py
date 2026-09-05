from inkex import Path, PathElement, Style
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from ..elements import iterate_nodes, nodes_to_elements
from ..elements.utils.stroke_to_satin import convert_path_to_satin
from ..svg import PIXELS_PER_MM


def element_outlines(group):
    outlines = []
    for element in nodes_to_elements(iterate_nodes(group)):
        if element.name == "SatinColumn":
            rail_pairs = zip(*element.plot_points_on_rails(
                0.3,
                element.pull_compensation_px,
                element.pull_compensation_percent / 100
            ))
            rails = [LineString(rail) for rail in rail_pairs]
            outlines.append(Polygon(list(rails[0].coords) + list(rails[1].reverse().coords)).buffer(0))
        elif element.name == "Stroke":
            outlines.append(element.as_multi_line_string().buffer(
                max(element.stroke_width / 2, 0.15 * PIXELS_PER_MM),
                cap_style="flat"
            ))
        elif element.name == "FillStitch":
            shape = element.shrink_or_grow_shape(element.shape, element.expand)
            outlines.extend(shape.geoms if hasattr(shape, "geoms") else [shape])
    return [outline for outline in outlines if not outline.is_empty]


def combined_outline(group, offset_mm):
    outlines = element_outlines(group)
    if not outlines:
        return None
    outline = unary_union(outlines).buffer(offset_mm * PIXELS_PER_MM)
    if outline.is_empty:
        return None
    return outline.buffer(0)


def combined_outlines(groups, offset_mm):
    outlines = []
    for group in groups:
        outlines.extend(element_outlines(group))
    if not outlines:
        return None
    outline = unary_union(outlines).buffer(offset_mm * PIXELS_PER_MM)
    if outline.is_empty:
        return None
    return outline.buffer(0)


def polygon_paths(shape):
    polygons = list(shape.geoms) if shape.geom_type == "MultiPolygon" else [shape]
    for polygon in polygons:
        if polygon.is_empty:
            continue
        yield list(polygon.exterior.coords)


def create_running_path(points, label, stitch_length_mm, color="#000000"):
    path = PathElement(attrib={"d": str(Path(points))})
    path.label = label
    path.set("style", Style({"fill": "none", "stroke": color}).to_str())
    path.set("inkstitch:stroke_method", "running_stitch")
    path.set("inkstitch:max_stitch_length_mm", str(stitch_length_mm))
    return path


def create_satin_path(points, label, width_mm, satin_method="satin_column", style_args=None, color="#000000"):
    if len(points) > 1 and points[0] == points[-1]:
        points = points[:-1]
    satin = convert_path_to_satin(
        points,
        width_mm * PIXELS_PER_MM,
        style_args or {},
        rungs_at_nodes=True
    )
    if satin is None:
        return None
    rails, rungs = satin
    path_data = ""
    for line in [*rails, *rungs]:
        path_data += "M" + " ".join(f"{x},{y}" for x, y in line) + " "
    path = PathElement(attrib={"d": path_data})
    path.label = label
    path.set("style", Style({"fill": "none", "stroke": color}).to_str())
    path.set("inkstitch:satin_column", "True")
    path.set("inkstitch:satin_method", satin_method)
    return path