
import numpy as np
import xml.etree.ElementTree
import warnings
import datetime
import lxml.etree
# import rasterio

def _load_calibration(path):
    """Load sentinel 1 calibration file as dictionary from PATH.

    The calibration file should be as included in .SAFE format
    retrieved from: https://scihub.copernicus.eu/

    Args:
        path: The path to the calibration file

    Returns:
        calibration: A dictionary with calibration constants
            {"abs_calibration_const": float(),
            "row": np.array(int),
            "col": np.array(int),
            "azimuth_time": np.array(np.datetime64),
            "sigma_0": np.array(float),
            "beta_0": np.array(float),
            "gamma": np.array(float),
            "dn": np.array(float),}

        info: A dictionary with the meta data given in 'adsHeader'
            {child[0].tag: child[0].text,
             child[1].tag: child[1].text,
             ...}
    """
    # open xml file
    tree = xml.etree.ElementTree.parse(path)
    root = tree.getroot()

    # Find info
    info_xml = root.findall('adsHeader')
    if len(info_xml) == 1:
        info = {}
        for child in info_xml[0]:
            info[child.tag] = child.text
    else:
        warnings.warn('Warning adsHeader not found')
        info = None

    # Find calibration list
    cal_vectors = root.findall('calibrationVectorList')
    if len(cal_vectors) == 1:
        cal_vectors = cal_vectors[0]
    else:
        warnings.warn('Error loading calibration list')
        return None, info

    # initialize arrays
    azimuth_time = np.array([], dtype=np.datetime64)
    line = np.array([], dtype=int)
    pixel = np.array([], dtype=int)
    sigma_0 = np.array([], dtype=float)
    beta_0 = np.array([], dtype=float)
    gamma = np.array([], dtype=float)
    dn = np.array([], dtype=float)

    # get data
    for cal_vec in cal_vectors:
        azimuth_time_i = np.datetime64(cal_vec[0].text)
        line_i = int(cal_vec[1].text)
        pixel_i = np.array(list(map(int, cal_vec[2].text.split())))
        sigma_0_i = np.array(list(map(float, cal_vec[3].text.split())))
        beta_0_i = np.array(list(map(float, cal_vec[4].text.split())))
        gamma_i = np.array(list(map(float, cal_vec[5].text.split())))
        dn_i = np.array(list(map(float, cal_vec[6].text.split())))

        # append the data
        azimuth_time = np.append(azimuth_time_i, np.repeat(azimuth_time_i, len(pixel_i)))
        line = np.append(line, np.repeat(line_i, len(pixel_i)))
        pixel = np.append(pixel, pixel_i)
        sigma_0 = np.append(sigma_0, sigma_0_i)
        beta_0 = np.append(beta_0, beta_0_i)
        gamma = np.append(gamma, gamma_i)
        dn = np.append(dn, dn_i)

    # Combine calibration info
    calibration = {
        "abs_calibration_const": float(root[1][0].text),
        "row": line,
        "col": pixel,
        "azimuth_time": azimuth_time,
        "sigma_0": sigma_0,
        "beta_0": beta_0,
        "gamma": gamma,
        "dn": dn,
    }

    return calibration, info


def _load_meta(SAFE_path):
    """Load manifest.safe as dictionary from SAFE_path.

    The manifest.safe file should be as included in .SAFE format
    retrieved from: https://scihub.copernicus.eu/

    Args:
        path: The path to the manifest.safe file

    Returns:
        metadata: A dictionary with meta_data
            example:
            {'nssdc_identifier': '2014-016A',
             'mission': 'SENTINEL-1A',
             'orbit_number': array([24062, 24062]),
             'relative_orbit_number': array([15, 15]),
             'phase_identifier': 1,
             'start_time': datetime.datetime(2018, 10, 9, 17, 14, 27, 947118),
             'stop_time': datetime.datetime(2018, 10, 9, 17, 14, 52, 945363),
             'pass': 'ASCENDING',
             'ascending_node_time': datetime.datetime(2018, 10, 9, 17, 2, 49, 152100),
             'start_time_ANX': 698795.0,
             'stop_time_ANX': 723793.2,
             'mode': 'IW',
             'swath': 'IW',
             'instrument_config': 6,
             'mission_data_ID': '172337',
             'polarisation': ['VV', 'VH'],
             'product_class': 'S',
             'product_composition': 'Slice',
             'product_type': 'GRD',
             'product_timeliness': 'Fast-24h',
             'slice_product_flag': 'true',
             'segment_start_time': datetime.datetime(2018, 10, 9, 17, 11, 29, 245933),
             'slice_number': 8,
             'total_slices': 16,
             'footprint': {'latitude': array([44.361824, 44.361824, 44.361824, 44.361824]),
              'longitude': array([8.145285, 8.145285, 8.145285, 8.145285])}}

            error: List of dictionary keys that was not found.
    """
    # Sorry the code look like shit but I do not like the file format
    # and I do not trust that ESA will keep the structure.
    # This is the reason for all the if statements and the error list

    # Open the xml like file
    with open(SAFE_path) as f:
        safe_test = f.read()
    safe_string = safe_test.encode(errors='ignore')
    safe_xml = lxml.etree.fromstring(safe_string)

    # Initialize results
    metadata = {}
    error = []

    # Prefixes used in the tag of the file. Do not ask me why the use them
    prefix1 = '{http://www.esa.int/safe/sentinel-1.0}'
    prefix2 = '{http://www.esa.int/safe/sentinel-1.0/sentinel-1}'
    prefix3 = '{http://www.esa.int/safe/sentinel-1.0/sentinel-1/sar/level-1}'

    # Put the data into the metadata

    # Get nssdc_identifier
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'nssdcIdentifier')]
    if len(values) == 1:
        metadata['nssdc_identifier'] = values[0].text
    else:
        error.append('nssdcIdentifier')

    # Get mission
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'familyName')]
    values2 = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'number')]
    if (len(values) > 0) & (len(values2) == 1):
        metadata['mission'] = values[0].text + values2[0].text
    else:
        error.append('mission')

    # get orbit_number
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'orbitNumber')]
    if len(values) == 2:
        metadata['orbit_number'] = np.array([int(values[0].text), int(values[1].text)])
    else:
        error.append('orbit_number')

    # get relative_orbit_number
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'relativeOrbitNumber')]
    if len(values) == 2:
        metadata['relative_orbit_number'] = np.array([int(values[0].text), int(values[1].text)])
    else:
        error.append('relative_orbit_number')

    # get phase_identifier
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'phaseIdentifier')]
    if len(values) == 1:
        metadata['phase_identifier'] = int(values[0].text)
    else:
        error.append('phase_identifier')

    # get start_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'startTime')]
    if len(values) == 1:
        t = values[0].text
        metadata['start_time'] = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]),
                                                   int(t[14:16]), int(t[17:19]), int(float(t[19:]) * 10 ** 6))
    else:
        error.append('start_time')

    # get stop_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix1 + 'stopTime')]
    if len(values) == 1:
        t = values[0].text
        metadata['stop_time'] = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]),
                                                  int(t[17:19]), int(float(t[19:]) * 10 ** 6))
    else:
        error.append('stop_time')

    # get pass
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + 'pass')]
    if len(values) == 1:
        metadata['pass'] = values[0].text
    else:
        error.append('pass')

    # get ascending_node_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + 'ascendingNodeTime')]
    if len(values) == 1:
        t = values[0].text
        metadata['ascending_node_time'] = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]),
                                                            int(t[14:16]), int(t[17:19]), int(float(t[19:]) * 10 ** 6))
    else:
        error.append('ascending_node_time')

    # get start_time_ANX
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + 'startTimeANX')]
    if len(values) == 1:
        metadata['start_time_ANX'] = float(values[0].text)
    else:
        error.append('start_time_ANX')

    # get stop_time_ANX
    values = [elem for elem in safe_xml.iterfind(".//" + prefix2 + 'stopTimeANX')]
    if len(values) == 1:
        metadata['stop_time_ANX'] = float(values[0].text)
    else:
        error.append('stop_time_ANX')

    # get mode
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'mode')]
    if len(values) == 1:
        metadata['mode'] = values[0].text
    else:
        error.append('mode')

    # get swath
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'swath')]
    if len(values) == 1:
        metadata['swath'] = values[0].text
    else:
        error.append('swath')

    # get instrument_config
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'instrumentConfigurationID')]
    if len(values) == 1:
        metadata['instrument_config'] = int(values[0].text)
    else:
        error.append('instrument_config')

    # get mission_data_ID
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'missionDataTakeID')]
    if len(values) == 1:
        metadata['mission_data_ID'] = values[0].text
    else:
        error.append('mission_data_ID')

    # get polarisation
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'transmitterReceiverPolarisation')]
    if len(values) == 2:
        metadata['polarisation'] = [values[0].text, values[1].text]
    else:
        error.append('polarisation')

    # get product_class
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'productClass')]
    if len(values) == 1:
        metadata['product_class'] = values[0].text
    else:
        error.append('product_class')

    # get product_composition
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'productComposition')]
    if len(values) == 1:
        metadata['product_composition'] = values[0].text
    else:
        error.append('product_composition')

    # get product_type
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'productType')]
    if len(values) == 1:
        metadata['product_type'] = values[0].text
    else:
        error.append('product_type')

    # get product_timeliness
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'productTimelinessCategory')]
    if len(values) == 1:
        metadata['product_timeliness'] = values[0].text
    else:
        error.append('product_timeliness')

    # get slice_product_flag
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'sliceProductFlag')]
    if len(values) == 1:
        metadata['slice_product_flag'] = values[0].text
    else:
        error.append('slice_product_flag')

    # get segment_start_time
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'segmentStartTime')]
    if len(values) == 1:
        t = values[0].text
        metadata['segment_start_time'] = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]),
                                                           int(t[14:16]), int(t[17:19]), int(float(t[19:]) * 10 ** 6))
    else:
        error.append('segment_start_time')

    # get slice_number
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'sliceNumber')]
    if len(values) == 1:
        metadata['slice_number'] = int(values[0].text)
    else:
        error.append('slice_number')

    # get total_slices
    values = [elem for elem in safe_xml.iterfind(".//" + prefix3 + 'totalSlices')]
    if len(values) == 1:
        metadata['total_slices'] = int(values[0].text)
    else:
        error.append('total_slices')

    # get footprint
    values = [elem for elem in safe_xml.iterfind(".//" + '{http://www.opengis.net/gml}coordinates')]
    if len(values) == 1:
        coordinates = values[0].text.split()
        lat = np.zeros(4)
        lon = np.zeros(4)
        for i in range(0, len(coordinates)):
            coord_i = coordinates[0].split(',')
            lat[i] = float(coord_i[0])
            lon[i] = float(coord_i[1])
        footprint = {'latitude': lat, 'longitude': lon}
        metadata['footprint'] = footprint
    else:
        error.append('footprint')

    return metadata, error


#def _load_annotation(path):

#    return annotation, info