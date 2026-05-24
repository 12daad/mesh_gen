import time
from typing import Sized
import itertools
import logging
import math

import numpy as np

from .image_util import ImageUtility


__all__ = ["GGRAY_CRITERIA_LIM", "mesh_gen_iter"]


GRAY_CRITERIA_LIM = .1
logger = logging.getLogger("mesh_gen")


def mesh_gen_iter(img_util: ImageUtility, batch_size: int = 4096, checked_gray: Sized[int] = None):
    if checked_gray is None:
        checked_gray = range(256)
    
    x_region: tuple = (.0, img_util.imag.shape[1] * img_util.scale)
    y_region: tuple = (.0, img_util.imag.shape[0] * img_util.scale)
    for gray, i in zip(checked_gray, range(len(checked_gray))):
        res = img_util._period_mapping(gray)
        batch_nx = math.ceil((x_region[1] - x_region[0]) / res / (batch_size-1))
        batch_ny = math.ceil((y_region[1] - y_region[0]) / res / (batch_size-1))
        logger.info(f"start generating mesh for {gray=}, total grays: {len(checked_gray)}, total batches {batch_nx*batch_ny}")
        x_collect = []
        y_collect = []
        for btx, bty in itertools.product(range(batch_nx), range(batch_ny)):
            t0 = time.time()
            x_start = x_region[0] + btx * batch_size * res
            y_start = y_region[0] + bty * batch_size * res
            x_end = min(x_start + batch_size * res - res, x_region[1])
            y_end = min(y_start + batch_size * res - res, y_region[1])
            x_lin = np.arange(x_start, x_end + res, res)
            y_lin = np.arange(y_start, y_end + res, res)
            xs, ys = np.meshgrid(x_lin, y_lin)
            index = np.abs(img_util.gray(xs, ys) - gray) < GRAY_CRITERIA_LIM
            xs = xs[index]
            ys = ys[index]
            x_collect.append(xs)
            y_collect.append(ys)
            dt_sec = time.time() - t0
            logger.info(f"{gray=}: {i+1}/{len(checked_gray)}, batch {btx*batch_nx + bty+1}/{batch_nx*batch_ny}, generate {len(xs)} points, consuming time: {dt_sec:.2f} sec")
        x_np = np.concatenate(x_collect)
        y_np = np.concatenate(y_collect)
        logger.info(f"{gray=} finished generating {len(x_np)} points")
        yield x_np, y_np, gray

