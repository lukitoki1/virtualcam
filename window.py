from PySide2.QtCore import QPoint, Qt
import PySide2.QtWidgets
import PySide2
import PySide2.QtGui
import numpy as np
import itertools

import math_utils


class Config:
    def __init__(self, config_dict: dict):
        self.colors = config_dict['colors']
        self.distance: int = config_dict.get('distance', 200)
        self.window_width: int = config_dict.get('window_width', 1024)
        self.window_height: int = config_dict.get('window_height', 768)
        self.move_step: int = config_dict.get('move_step', 1)
        self.rotate_step: int = config_dict.get('rotate_step', 30)
        self.zoom_step: int = config_dict.get('zoom_step', 20)


class WindowHandler(PySide2.QtWidgets.QMainWindow):
    def __init__(self, polygons: np.array, config: Config):
        super().__init__()

        self.polygons = polygons
        self.config = config

        self.keyboard_handler = KeyboardHandler(self.config.move_step, self.config.rotate_step, self.config.zoom_step)
        self.mouse_handler = MouseHandler(self.config.rotate_step, self.config.zoom_step)

        self.prepare_window()

    def prepare_window(self):
        self.setFixedSize(self.config.window_width, self.config.window_height)
        self.setWindowTitle("VirtualCam")

    def paintEvent(self, event: PySide2.QtGui.QPaintEvent):
        self.painter = PySide2.QtGui.QPainter(self)
        self.painter.translate(self.config.window_width / 2, self.config.window_height / 2)
        self.painter.scale(1, -1)
        self.project_polygons()
        self.painter.end()

    def keyPressEvent(self, event: PySide2.QtGui.QKeyEvent):
        key = event.key()
        if key == Qt.Key_W:
            self.polygons = self.keyboard_handler.z_move_forward(self.polygons)
        elif key == Qt.Key_S:
            self.polygons = self.keyboard_handler.z_move_backward(self.polygons)
        elif key == Qt.Key_A:
            self.polygons = self.keyboard_handler.x_move_left(self.polygons)
        elif key == Qt.Key_D:
            self.polygons = self.keyboard_handler.x_move_right(self.polygons)
        elif key == Qt.Key_Q:
            self.polygons = self.keyboard_handler.y_move_up(self.polygons)
        elif key == Qt.Key_E:
            self.polygons = self.keyboard_handler.y_move_down(self.polygons)
        elif key == Qt.Key_Up:
            self.polygons = self.keyboard_handler.x_rotate_up(self.polygons)
        elif key == Qt.Key_Down:
            self.polygons = self.keyboard_handler.x_rotate_down(self.polygons)
        elif key == Qt.Key_Left:
            self.polygons = self.keyboard_handler.y_rotate_left(self.polygons)
        elif key == Qt.Key_Right:
            self.polygons = self.keyboard_handler.y_rotate_right(self.polygons)
        elif key == Qt.Key_Z:
            self.polygons = self.keyboard_handler.z_rotate_left(self.polygons)
        elif key == Qt.Key_X:
            self.polygons = self.keyboard_handler.z_rotate_right(self.polygons)
        elif key == Qt.Key_C:
            self.config.distance = self.keyboard_handler.zoom_in(self.config.distance)
        elif key == Qt.Key_V:
            self.config.distance = self.keyboard_handler.zoom_out(self.config.distance)

        event.accept()
        self.repaint()

    def mousePressEvent(self, event: PySide2.QtGui.QMouseEvent):
        self.mouse_handler.reset_mouse_pos()

    def mouseMoveEvent(self, event: PySide2.QtGui.QMouseEvent):
        self.polygons = self.mouse_handler.move(self.polygons, event.pos())
        self.repaint()

    def wheelEvent(self, event: PySide2.QtGui.QWheelEvent):
        self.config.distance = self.mouse_handler.zoom(self.config.distance, event.delta())
        self.repaint()

    def draw_polygons(self, polygon_projections: np.array):
        for i, polygon in enumerate(polygon_projections):
            points = itertools.cycle(polygon)
            point_1 = next(points)
            for _ in range(len(polygon)):
                point_2 = next(points)
                self.painter.setPen(self.parse_color(i))
                self.painter.drawLine(point_1, point_2)
                point_1 = point_2

    def parse_color(self, polygon_no: int):
        color_str = self.config.colors[polygon_no]
        if color_str == 'red':
            return Qt.red
        elif color_str == 'blue':
            return Qt.blue
        return Qt.black

    def project_polygons(self):
        polygon_projections = math_utils.project_polygons(self.polygons, self.config.distance)
        self.draw_polygons(polygon_projections)


class KeyboardHandler:
    def __init__(self, move_step: int, rotate_ste: int, zoom_step: int):
        self.move_step, self.rotate_step, self.zoom_step = move_step, rotate_ste, zoom_step

    def x_move_left(self, polygons: np.array) -> np.array:
        return math_utils.move_polygons(polygons, x=1, step=self.move_step)

    def x_move_right(self, polygons: np.array) -> np.array:
        return math_utils.move_polygons(polygons, x=-1, step=self.move_step)

    def y_move_up(self, polygons: np.array) -> np.array:
        return math_utils.move_polygons(polygons, y=-1, step=self.move_step)

    def y_move_down(self, polygons: np.array) -> np.array:
        return math_utils.move_polygons(polygons, y=1, step=self.move_step)

    def z_move_forward(self, polygons: np.array) -> np.array:
        return math_utils.move_polygons(polygons, z=-1, step=self.move_step)

    def z_move_backward(self, polygons: np.array) -> np.array:
        return math_utils.move_polygons(polygons, z=1, step=self.move_step)

    def x_rotate_up(self, polygons: np.array) -> np.array:
        return math_utils.rotate_polygons(polygons, x=1, step=self.rotate_step)

    def x_rotate_down(self, polygons: np.array) -> np.array:
        return math_utils.rotate_polygons(polygons, x=-1, step=self.rotate_step)

    def y_rotate_left(self, polygons: np.array) -> np.array:
        return math_utils.rotate_polygons(polygons, y=1, step=self.rotate_step)

    def y_rotate_right(self, polygons: np.array) -> np.array:
        return math_utils.rotate_polygons(polygons, y=-1, step=self.rotate_step)

    def z_rotate_left(self, polygons: np.array) -> np.array:
        return math_utils.rotate_polygons(polygons, z=1, step=self.rotate_step)

    def z_rotate_right(self, polygons: np.array) -> np.array:
        return math_utils.rotate_polygons(polygons, z=-1, step=self.rotate_step)

    def zoom_in(self, distance: int) -> int:
        return math_utils.zoom_polygons(distance, 1, self.zoom_step)

    def zoom_out(self, distance: int) -> int:
        return math_utils.zoom_polygons(distance, -1, self.zoom_step)


class MouseHandler:
    def __init__(self, rotate_step: int, zoom_step: int):
        self.rotate_step, self.zoom_step = rotate_step, zoom_step
        self.__last_mouse_pos = None
        self.mouse_sensitivity = 0.1

    def reset_mouse_pos(self):
        self.__last_mouse_pos = None

    def move(self, polygons: np.array, mouse_pos: QPoint) -> np.array:
        if self.__last_mouse_pos:
            shift: QPoint = mouse_pos - self.__last_mouse_pos
            polygons = math_utils.rotate_polygons(polygons, x=shift.y() * self.mouse_sensitivity, y=shift.x() * self.mouse_sensitivity, step=self.rotate_step)
        self.__last_mouse_pos = mouse_pos
        return polygons

    def zoom(self, distance: int, delta: int) -> int:
        return math_utils.zoom_polygons(distance, 1, self.zoom_step) if delta > 0 else \
            math_utils.zoom_polygons(distance, -1, self.zoom_step)
