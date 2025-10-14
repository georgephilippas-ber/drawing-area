from typing import Tuple, List

from ezdxf import readfile
from ezdxf.entities import Hatch, EdgePath
from shapely.geometry import Polygon

from dataclasses import dataclass

ENVELOPE_DETAIL_LINE_LAYER: str = "LINE-1"
EXTERIOR_WALLS_LAYER_HATCH_DEFAULT: str = "A-WALL-PATT-Exterior-1"
FILLED_REGION_LAYER_DEFAULT: str = "A-DETL-GENF-1"


def plane_point(space_point: Tuple[float, float, float]) -> Tuple[float, float]:
    return space_point[0], space_point[1]


def polygon_from_hatch(hatch: Hatch, insert_point: Tuple[float, float] = (0., 0.)) -> Polygon:
    path_: EdgePath = hatch.paths[0]

    vertices_ = []
    for edge_ in path_:
        vertices_.append((edge_.start_point.x + insert_point[0], edge_.start_point.y + insert_point[1]))

    return Polygon(vertices_)


def get_hatch_area(hatch: Hatch) -> float:
    return polygon_from_hatch(hatch).area


@dataclass
class Area:
    net_area: float
    exterior_walls_area: float


def get_net_area(filename: str, *, exterior_walls_layer_: str = ENVELOPE_DETAIL_LINE_LAYER,
                 exterior_walls_layer_hatch_: str = EXTERIOR_WALLS_LAYER_HATCH_DEFAULT,
                 filled_region_layer_: str = FILLED_REGION_LAYER_DEFAULT
                 ) -> Area:
    document = readfile(filename)
    modelspace = document.modelspace()

    exterior_wall_lines_ = []
    for entity_ in modelspace:
        if entity_.dxf.layer == exterior_walls_layer_ and entity_.dxftype() == "LINE":
            exterior_wall_lines_.append(entity_)

    exterior_wall_points_ = []
    for line_ in exterior_wall_lines_:
        exterior_wall_points_.append(plane_point(line_.dxf.start))

    envelope_area_ = Polygon(exterior_wall_points_).area * 1.e-6

    wall_polygons_: List[Polygon] = []
    wall_area_ = 0.
    for entity_ in modelspace:
        if entity_.dxf.layer == exterior_walls_layer_hatch_:
            if isinstance(entity_, Hatch):
                wall_area_ += get_hatch_area(entity_)
                wall_polygons_.append(polygon_from_hatch(entity_))
    wall_area_ *= 1.e-6

    net_ = envelope_area_ - wall_area_

    negative_area_ = 0.
    for entity_ in modelspace:
        if entity_.dxf.layer == filled_region_layer_:
            if isinstance(entity_, Hatch):
                negative_area_ += abs(polygon_from_hatch(entity_).area) * 1.e-6

    final_ = net_ - negative_area_

    return Area(final_, wall_area_)
