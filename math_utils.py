import numpy as np
from PySide2.QtCore import QPointF


class Axis:
    X = 'x'
    Y = 'y'
    Z = 'z'


def move_polygons(polygons: np.array, x: int = 0, y: int = 0, z: int = 0, step: int = 0) -> np.array:
    def move_x():
        base[0, 3] = __calculate_move_shift(x, step)

    def move_y():
        base[1, 3] = __calculate_move_shift(y, step)

    def move_z():
        base[2, 3] = __calculate_move_shift(z, step)

    base = __create_base()
    move_x(), move_y(), move_z()
    return calculate_polygons(polygons, base)


def rotate_polygons(polygons: np.array, x: int = 0, y: int = 0, z: int = 0, step: int = 0) -> np.array:
    polygons = _rotate_polygons(polygons, Axis.X, x, step)
    polygons = _rotate_polygons(polygons, Axis.Y, y, step)
    return _rotate_polygons(polygons, Axis.Z, z, step)


def zoom_polygons(distance: int, shift: int = 0, step: int = 0) -> int:
    return distance + __calculate_zoom_shift(shift, step)


def _rotate_polygons(polygons: np.array, axis: Axis, shift: int, step: int = 0) -> np.array:
    def rotate_x():
        base[1:3, 1:3] = np.array([
            [np.cos(angle_shift), -np.sin(angle_shift)],
            [np.sin(angle_shift), np.cos(angle_shift)]
        ])

    def rotate_y():
        base[0:3:2, 0:3:2] = np.array([
            [np.cos(angle_shift), np.sin(angle_shift)],
            [-np.sin(angle_shift), np.cos(angle_shift)]
        ])

    def rotate_z():
        base[0:2, 0:2] = np.array([
            [np.cos(angle_shift), -np.sin(angle_shift)],
            [np.sin(angle_shift), np.cos(angle_shift)]
        ])

    angle_shift = __calculate_angle_shift(shift, step)
    base = __create_base()
    if axis == Axis.X:
        rotate_x()
    elif axis == Axis.Y:
        rotate_y()
    elif axis == Axis.Z:
        rotate_z()
    return calculate_polygons(polygons, base)


def calculate_polygons(polygons: np.array, base: np.array) -> np.array:
    def calculate_points(polygon: np.array) -> np.array:
        return np.array(list(map(lambda xyz: np.matmul(base, np.append(xyz, 1))[:3], polygon)))

    return np.array(list(map(lambda polygon: calculate_points(polygon), polygons)))


def project_polygons(polygons: np.array, distance: int) -> np.array:
    def project_point(x: int, y: int, z: int) -> QPointF:
        z = 0.00001 if z <= 0 else z
        x *= distance / z
        y *= distance / z
        return QPointF(x, y)

    def project_points(polygon: np.array) -> np.array:
        return np.array(list(map(lambda point: project_point(*point), polygon)))

    return np.array(list(map(lambda polygon: project_points(polygon), polygons)))


def __calculate_move_shift(shift: int, step: int) -> int:
    return step * shift


def __calculate_angle_shift(shift: int, step: int) -> int:
    return np.pi / step * shift


def __calculate_zoom_shift(shift: int, step: int) -> int:
    return __calculate_move_shift(shift, step)


def __create_base() -> np.array:
    return np.eye(4)
