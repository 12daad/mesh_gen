
import enum
from typing import Sized, ClassVar
import os
import logging

import gdstk

logger = logging.getLogger("gds_util")


__all__ = ["GdsCellType", "GdsLibrary"]

class GdsCellType(enum.Enum):
    RECTANGLE = "rectangle"

    _names : ClassVar[set[str]] = set()
    
    @staticmethod
    def create(cell_type: GdsCellType, name: str = None, **kwargs) -> gdstk.Cell:
        if cell_type == GdsCellType.RECTANGLE:
            width = kwargs.get('width', None)
            height = kwargs.get('height', None)
            layer = kwargs.get('layer', 0)
            if name is None:
                name = f"{cell_type.value}_{layer}"
                logging.warning(f"not sepcify name, using name {name}")
            if width is None or height is None:
                raise ValueError("Width and height must be provided for rectangle cell type.")

            cell = gdstk.Cell(name)
            comp = gdstk.rectangle((0, 0), (width, height), layer=layer)
            cell.add(comp)
            return cell
        else:
            raise NotImplementedError(f"Unsupported cell type: {cell_type}")


class GdsLibrary:
    def __init__(self):
        self.lib = gdstk.Library()
        self.cell: list[gdstk.Cell] = []
        self.device = gdstk.Cell("DEVICE")
        self.lib.add(self.device)
    
    def create_cell(self, cell_type: GdsCellType, name=None, **kwargs) -> gdstk.Cell:
        cell = GdsCellType.create(cell_type, name, **kwargs)
        self.cell.append(cell)
        self.lib.add(cell)
        logger.info(f"Cell {cell.name} created with parameters: {kwargs}")
        return cell
    
    def add_ref_multi_xy(self, cell: gdstk.Cell, x : Sized[float], y: Sized[float], rotation: float = 0.0, magnification: float = 1.0) -> list[gdstk.Reference]:
        if cell not in self.cell:
            raise ValueError("The cell must be created by this library before adding reference.")
        refs = []
        logger.info(f"Adding references of cell '{cell.name}' at multiple coordinates with rotation {rotation} and magnification {magnification}. Total points: {len(x)}")
        for xy in zip(x, y):
            ref = gdstk.Reference(cell, origin=xy)
            ref.rotation = rotation
            ref.magnification = magnification
            refs.append(ref)
        self.device.add(*refs)
        logger.info(f"Added {len(refs)} references of cell '{cell.name}' at specified coordinates with rotation {rotation} and magnification {magnification}.")
        return refs

    def add_ref(self, cell: gdstk.Cell, xy: tuple[float, float], rotation: float = 0.0, magnification: float = 1.0) -> gdstk.Reference:
        if cell not in self.cell:
            raise ValueError("The cell must be created by this library before adding reference.")
        ref = gdstk.Reference(cell, origin=xy)
        ref.rotation = rotation
        ref.magnification = magnification
        self.device.add(ref)
        return ref

    def dump(self, filename):
        try:
            self.lib.write_gds(filename)
            logger.info(f"GDS file '{filename}' has been successfully written to `{os.path.abspath(filename)}`")
        except IOError as e:
            logger.error(f"Failed to write GDS file '{filename}': {e}")
