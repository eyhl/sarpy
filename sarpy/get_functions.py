from scipy import interpolate
import warnings


def get_index(lat, long, lat_gridpoints, long_gridpoints, row_gridpoints, column_gridpoints):
    """Get index of a location by interpolating grid-points

    Args:
        lat(number): Latitude of the location
        long(number): Longitude of location
        lat_gridpoints(numpy array of length n): Latitude of grid-points
        long_gridpoints(numpy array of length n): Longitude of grid-points
        row_gridpoints(numpy array of length n): row of grid-points
        column_gridpoints(numpy array of length n): column of grid-points

    Returns:
        row(int): The row index of the location
        column(int): The column index of the location

    Raises:
    """

    # Create interpolate functions
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f_row = interpolate.interp2d(lat_gridpoints, long_gridpoints, row_gridpoints)
        f_column = interpolate.interp2d(lat_gridpoints, long_gridpoints, column_gridpoints)

    # get index
    row = int(round(f_row(lat, long)[0]))
    column = int(round(f_column(lat, long)[0]))

    return row, column


def get_coordinate(row, column, lat_gridpoints, long_gridpoints, row_gridpoints, column_gridpoints):
    """Get coordinate from index by interpolating grid-points

    Args:
        row(number): index of the row of interest position
        column(number): index of the column of interest position
        lat_gridpoints(numpy array of length n): Latitude of grid-points
        long_gridpoints(numpy array of length n): Longitude of grid-points
        row_gridpoints(numpy array of length n): row of grid-points
        column_gridpoints(numpy array of length n): column of grid-points

    Returns:
        lat(float): Latitude of the position
        long(float): longitude of the position

    Raises:
    """

    # Create interpolate functions
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f_lat = interpolate.interp2d(row_gridpoints, column_gridpoints, lat_gridpoints)
        f_long = interpolate.interp2d(row_gridpoints, column_gridpoints, long_gridpoints)

    # get coordinates
    lat = f_lat(row, column)[0]
    long = f_long(row, column)[0]

    return lat, long

