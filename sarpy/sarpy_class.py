import numpy as np
import warnings
from . import get_functions
# TODO: Decide the amount of checking and control in the class


class SarImage:
    """ Class to contain SAR image, relevant meta data and methods.

    Attributes:
        bands(list of numpy arrays): The measurements.
        mission(str): Mission name:
        time(datetime): start time of acquisition
        footprint(dict): dictionary with footprint of image
                        footprint = {'latitude': np.array
                                    'longitude': np.array}
        product_meta(dict): Dictionary with meta data.
        band_names(list of str): Names of the band. Normally the polarisation.
        calibration(list of dict): Dictionary with calibration information for each band.
        geo_tie_point(list of dict): Dictionary with geo tie point for each band.
        band_meta(list of dict): Dictionary with meta data for each band.
    """

    def __init__(self, bands, mission=None, time=None, footprint=None, product_meta=None,
                 band_names=None, calibration=None, geo_tie_point=None, band_meta=None, **kwargs):

        # assign values
        self.bands = bands
        self.mission = mission
        self.time = time
        self.footprint = footprint
        self.product_meta = product_meta
        self.band_names = band_names
        self.calibration = calibration
        self.geo_tie_point = geo_tie_point
        self.band_meta = band_meta
        # Note that SlC is in strips. Maybe load as list of images

    def get_index(self, lat, long):
        """Get index of a location by interpolating grid-points

        Args:
            lat(number): Latitude of the location
            long(number): Longitude of location

        Returns:
            row(int): The row index of the location
            column(int): The column index of the location

        Raises:
        """
        geo_tie_point = self.geo_tie_point
        row = np.zeros(len(geo_tie_point), dtype=int)
        column = np.zeros(len(geo_tie_point), dtype=int)

        # find index for each band
        for i in range(len(geo_tie_point)):
            lat_grid = geo_tie_point[i]['latitude']
            long_grid = geo_tie_point[i]['longitude']
            row_grid = geo_tie_point[i]['row']
            column_grid = geo_tie_point[i]['column']
            row[i], column[i] = get_functions.get_index(lat, long, lat_grid, long_grid, row_grid, column_grid)

        # check that the results are the same
        if (abs(row.max() - row.min()) > 0.5) or (abs(column.max() - column.min()) > 0.5):
            warnings.warn('Warning different index found for each band. First index returned')

        return row[0], column[0]

    def get_coordinate(self, row, column):
        """Get coordinate from index by interpolating grid-points

            Args:
                row(number): index of the row of interest position
                column(number): index of the column of interest position

            Returns:
                lat(float): Latitude of the position
                long(float): longitude of the position

            Raises:
            """

        geo_tie_point = self.geo_tie_point
        lat = np.zeros(len(geo_tie_point), dtype=float)
        long = np.zeros(len(geo_tie_point), dtype=float)

        # find index for each band
        for i in range(len(geo_tie_point)):
            lat_grid = geo_tie_point[i]['latitude']
            long_grid = geo_tie_point[i]['longitude']
            row_grid = geo_tie_point[i]['row']
            column_grid = geo_tie_point[i]['column']
            lat[i], long[i] = get_functions.get_coordinate(row, column, lat_grid, long_grid, row_grid, column_grid)

        # check that the results are the same
        if (abs(lat.max() - lat.min()) > 0.001) or (abs(long.max() - long.min()) > 0.001):
            warnings.warn('Warning different coordinates found for each band. Mean returned')

        return lat.mean(), long.mean()

