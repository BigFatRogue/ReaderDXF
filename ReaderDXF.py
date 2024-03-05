import math
from tqdm import tqdm

import ezdxf
from ezdxf import colors
import pickle
from Objects2D import *
from function import try_error


def len_vec(x: float, y: float) -> float:
    """Длина вектора"""
    return math.sqrt(x ** 2 + y ** 2)


def solver_quadratic(b: float, c: float) -> tuple:
    """
    Решение квадратного уравнения. a = 1
    :param b, c: коэффициенты квадратного уравнение
    :return: корни уравнение
    """
    D = b ** 2 - 4 * c
    x1 = (-b + math.sqrt(D)) / 2
    x2 = (-b - math.sqrt(D)) / 2
    return x1, x2


def ellipse_autocad_to_pyqt(obj) -> dict:
    def calculation_angel_item(vector: Vec2) -> float:
        """
        Угол под которым накланён эллипс относительно оси Ox
        :param vector_major: вектор большой оси. x1 - x0, y1 - y0.
        :return: Угол в градусах. Получаю угол, для вращения item ПРОТИВ ЧАСОВО СТРЕЛКИ в PyQt
        """
        vec_x, vec_y = vector.x, vector.y

        if vec_y > 0:
            return vector.angle_between(Vec2(-1, 0))
        elif vec_y < 0:
            return -vector.angle_between(Vec2(-1, 0))
        elif vec_y == 0 and vec_x > 0:
            return -180
        return 0

    def calculation_end_angel(angle) -> float:
        if angle > 180:
            return 360 - angle + 180
        elif angle < 180:
            return 360 - angle - 180
        return 0

    x0, y0, _ = obj.construction_tool().center
    major_vec_x, major_vec_y, _ = obj.construction_tool().major_axis
    minor_vec_x, minor_vec_y, _ = obj.construction_tool().minor_axis

    start_x, start_y, _ = obj.construction_tool().start_point
    end_x, end_y, _ = obj.construction_tool().end_point

    start_param_degree = obj.dxf.start_param/math.pi * 180
    end_param_degree = obj.dxf.end_param/math.pi * 180
    len_arc = end_param_degree - start_param_degree

    vec_minor = Vec2(minor_vec_x, minor_vec_y)
    vec_major = Vec2(major_vec_x, major_vec_y)
    alpha = calculation_angel_item(vector=vec_major)
    end_angle = calculation_end_angel(angle=end_param_degree)

    w = vec_minor.len()
    h = vec_major.len()

    return {"center": (x0, y0), "w": w, "h": h, "alpha": alpha, "start_angle": end_angle, "len_arc": len_arc}


def save_mp(model_space):
    with open('model_space.bin', 'wb') as file:
        pickle.dump(model_space, file)


def load_mp() -> ModelSpace:
    with open('model_space.bin', 'rb') as file:
        dxf = pickle.load(file)
    return dxf


def convert_dxf_object(doc, obj, scale=None, color_block=7) -> DxfObject:
    tp = obj.dxftype()

    color_acad = obj.dxf.color
    if color_acad == 256:       # ПО СЛОЮ
        real_color = doc.layers.get(obj.dxf.layer).color
    elif color_acad == 0:      # ПО БЛОКУ
        real_color = color_block
    else:
        real_color = color_acad
    color = colors.DXF_DEFAULT_COLORS[real_color]

    lineweight = obj.dxf.lineweight
    linetype = obj.dxf.linetype

    if tp == 'INSERT':
        x0, y0, _ = obj.dxf.insert
        name = obj.dxf.name
        scale = Vec2(obj.dxf.xscale, obj.dxf.yscale)
        block_object = Block((x0, y0), name)

        for attr in obj.attribs:
            tag = attr.dxf.tag
            value = attr.dxf.text
            block_object.add_attribute(tag, value)

        block = doc.blocks[obj.dxf.name]
        for obj_in_block in block:
            if obj_in_block.dxftype() != 'ATTDEF':
                block_object.add_object(
                    convert_dxf_object(doc=doc, obj=obj_in_block, scale=scale, color_block=real_color))
        return block_object

    elif tp == 'LINE':
        x0, y0, _ = obj.dxf.start
        x1, y1, _ = obj.dxf.end

        new_line = Line(pos0=(x0, y0), pos1=(x1, y1), scale=scale,
                        linetype=linetype, color=color, lineweight=lineweight)
        return new_line

    elif tp == 'POLYLINE':
        return DxfObject()

    elif tp == 'LWPOLYLINE':
        new_polyline = Polyline()

        count_line = len(obj)
        k = 0
        for i, (x0, y0, start_width, end_width, bulge) in enumerate(obj):
            x1, y1, *_ = obj[(i + 1) % count_line]

            if i < count_line - 1:
                pos0, pos1 = (x0, y0), (x1, y1)
            else:
                if obj.dxf.flags == 1 or obj.closed:
                    pos0, pos1 = (x0, y0), (x1, y1)
                    k = 360

            if bulge:
                midpoint, start_angle, end_angle, radius = ezdxf.math.bulge_to_arc(pos0, pos1, bulge)
                center = ezdxf.math.bulge_center(pos0, pos1, bulge)
                new_arc = Acr(center=center, radius=radius, start_angle=math.degrees(start_angle), end_angle=k + math.degrees(end_angle),
                              scale=scale, color=color,  lineweight=lineweight,  pos0=(x0, y0))
                new_polyline.add_object(new_arc)
            else:
                new_line = Line(pos0=pos0, pos1=pos1, scale=scale,
                                linetype=linetype, color=color, lineweight=lineweight)
                new_polyline.add_object(new_line)

        return new_polyline

    elif tp == 'CIRCLE':
        x0, y0, _ = obj.dxf.center
        radius = obj.dxf.radius
        new_circle = Circle(center=(x0, y0), radius=radius, scale=scale,
                            color=color, lineweight=lineweight)
        return new_circle

    elif tp == 'ARC':
        x0, y0, _ = obj.dxf.center
        radius = obj.dxf.radius
        start_angle = obj.dxf.start_angle
        end_angle = obj.dxf.end_angle
        len_arc = -(360 - start_angle + end_angle) if start_angle > 180 else -(end_angle - start_angle)
        start_angle = 360 - start_angle if start_angle > 180 else -start_angle

        return EllipseArc(center=(x0, y0), start_angle=start_angle, len_arc=len_arc,
                          w=radius, h=radius, scale=scale, color=color, lineweight=lineweight, alpha=0)


    elif tp == 'ELLIPSE':
        dct = ellipse_autocad_to_pyqt(obj)

        return EllipseArc(scale=scale, color=color, lineweight=lineweight, **dct)

    elif tp == 'TEXT':
        x0, y0, _ = obj.dxf.insert
        text = obj.dxf.text
        height = obj.dxf.height
        new_text = Text((x0, y0), text, height, color)
        return DxfObject()

    elif tp == 'MTEXT':
        x, y, _ = obj.dxf.insert
        text = obj.dxf.text
        height = obj.dxf.char_height
        attachment_point = obj.dxf.attachment_point
        new_text = Text((x, y), text, height, color)
        return DxfObject()

    elif tp == 'SPLINE':
        fit_points = tuple((x, y) for x, y, _ in obj.fit_points)
        control_points = tuple((x, y) for x, y, _ in obj.control_points)
        return DxfObject()

    else:
        return DxfObject()


def create_msp(filepath: str) -> ModelSpace:
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()
    mp = ModelSpace()

    for msp_obj in msp:
        my_obj = convert_dxf_object(doc, msp_obj)
        mp.add(my_obj)

    return mp


if __name__ == '__main__':
    # dxf = r'dxf_files/block.dxf'
    dxf = r'dxf_files/Зона_101_Отделение_приёмки_сырого_молока_03_02_23.dxf'
    model_space: ModelSpace = create_msp(dxf)
    # b: Block = model_space[2]

    # save_mp(model_space)
    # model_space: ModelSpace = load_mp()

