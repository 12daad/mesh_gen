
import numpy as np


__all__ = ["LinearGrayPeriodMapping", "ImageUtility"]

class GrayPeriodMapping:
    def __call__(self, *args, **kwds):
        raise NotImplementedError("Please implement the __call__ method to return the period mapping for given gray levels.")

class LinearGrayPeriodMapping(GrayPeriodMapping):
    def __init__(self, min_period, max_period):
        self.min_period = min_period
        self.max_period = max_period
        self.periods = np.arange(256) * (max_period-min_period) / 255 + min_period
    
    def __call__(self, gray_levels:np.ndarray):
        return self.periods[gray_levels]
    
class GammaGrayPeriodMapping(GrayPeriodMapping):
    def __init__(self, min_period, max_period, gamma):
        self.min_period = min_period
        self.max_period = max_period
        self.gamma = gamma
        self.periods = min_period + (max_period - min_period) * np.arange(256) ** gamma
    
    def __call__(self, gray_levels: np.ndarray):
        return self.periods(gray_levels)

class CustomGrayPeriodMapping(GrayPeriodMapping):
    def __init__(self, periods):
        self.periods = np.array(periods)

    def __call__(self, gray_levels):
        return self.periods[gray_levels]

class ImageUtility:
    def __init__(self, imag: np.ndarray, scale: float, period_mapping: GrayPeriodMapping):
        self._period_mapping = period_mapping
        self.imag: np.ndarray = imag
        self.scale = scale
        
    def period(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self._period_mapping(self.gray(x, y))
    
    def gray(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        row = (y/self.scale) \
                    .clip(0, self.imag.shape[0] - 1) \
                    .round().astype(np.int32)
        col = (x/self.scale) \
                    .clip(0, self.imag.shape[1] - 1) \
                    .round().astype(np.int32)
        return self.imag[row,col]
    
