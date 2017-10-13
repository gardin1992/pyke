import copy
import numpy as np
from scipy import signal
from astropy.io import fits
from tqdm import tqdm

__all__ = ['LightCurve', 'KeplerLightCurveFile']


class LightCurve(object):
    """
    Implements a basic time-series class for a generic lightcurve.

    Attributes
    ----------
    time : array-like
        Time-line
    flux : array-like
        Data flux for every time point
    flux_err : array-like
        Uncertainty in each flux data point
    quality : array-like
        Array indicating the quality of each data point
    centroid_col, centroid_row : array-like, array-like
        Centroid column and row coordinates as a function of time
    """

    def __init__(self, time, flux, flux_err=None, quality=None, centroid_col=None,
                 centroid_row=None):
        self.time = time
        self.flux = flux
        self.flux_err = flux_err
        self.quality = quality
        self.centroid_col = centroid_col
        self.centroid_row = centroid_row

    def stitch(self, *others):
        """
        Stitches LightCurve objects.

        Parameters
        ----------
        *others : LightCurve objects
            Light curves to be stitched.

        Returns
        -------
        stitched_lc : LightCurve object
            Stitched light curve.
        """
        time = self.time
        flux = self.flux
        flux_err = self.flux_err
        quality = self.quality
        centroid_col = self.centroid_col
        centroid_row = self.centroid_row

        for i in range(len(others)):
            time = np.append(time, others[i].time)
            flux = np.append(flux, others[i].flux)
            flux_err = np.append(flux_err, others[i].flux_err)
            quality = np.append(quality, others[i].quality)
            centroid_col = np.append(centroid_col, others[i].centroid_col)
            centroid_row = np.append(centroid_row, others[i].centroid_row)

        return LightCurve(time=time, flux=flux, flux_err=flux_err,
                          quality=quality, centroid_col=centroid_col,
                          centroid_row=centroid_row)

    def flatten(self, window_length=101, polyorder=3, **kwargs):
        """
        Removes low frequency trend using scipy's Savitzky-Golay filter.

        Parameters
        ----------
        window_length : int
            The length of the filter window (i.e. the number of coefficients).
            ``window_length`` must be a positive odd integer.
        polyorder : int
            The order of the polynomial used to fit the samples. ``polyorder``
            must be less than window_length.
        **kwargs : dict
            Dictionary of arguments to be passed to `scipy.signal.savgol_filter`.

        Returns
        -------
        flatten : LightCurve object
            Flattened lightcurve
        trend : LightCurve object
            Trend in the lightcurve data
        """
        trend = signal.savgol_filter(x=self.flux, window_length=window_length,
                                     polyorder=polyorder, **kwargs)
        flatten = copy.copy(self)
        flatten.flux = self.flux / trend
        flatten.flux_err = self.flux_err / trend
        trend = copy.copy(self)
        trend.flux = trend

        return flatten, trend

    def fold(self, phase, period):
        return LightCurve(((self.time - phase + 0.5 * period) / period) % 1 - 0.5, self.flux)

    def draw(self):
        raise NotImplementedError("Should we implement a LightCurveDrawer class?")

    def to_csv(self):
        raise NotImplementedError()

    def to_fits(self):
        raise NotImplementedError()


class KeplerLightCurveFile(object):

    def __init__(self, path, **kwargs):
        self.hdu = fits.open(path, **kwargs)

    def get_lightcurve(self, flux_type, centroid_type='MOM_CENTR'):
        if flux_type in self._flux_types():
            return LightCurve(self.hdu[1].data['TIME'], self.hdu[1].data[flux_type],
                              flux_err=self.hdu[1].data[flux_type + "_ERR"],
                              quality=self.hdu[1].data['QUALITY'],
                              centroid_col=self.hdu[1].data[centroid_type + "1"],
                              centroid_row=self.hdu[1].data[centroid_type + "2"])
        else:
            raise KeyError("{} is not a valid flux type. Available types are: {}".
                           format(flux_type, self._flux_types))
    @property
    def SAP_FLUX(self):
        return self.get_lightcurve('SAP_FLUX')

    @property
    def PDCSAP_FLUX(self):
        return self.get_lightcurve('PDCSAP_FLUX')

    def _flux_types(self):
        """Returns a list of available flux types for this light curve file"""
        return [n for n in  self.hdu[1].data.columns.names if 'FLUX' in n]


class Detrender(object):
    """
    """
    def detrend(self):
        """
        Returns a LightCurve object
        """
        pass


class ArcLengthDetrender(Detrender):
    def detrend(time, flux):
        pass