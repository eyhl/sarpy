
import numpy as np
import xml.etree.ElementTree
# import rasterio
# import warnings


def _load_calibration(path):
    '''
    Loads xml file from path and returns the information as dic's.
    input:

    output:
    '''
    # open xml file
    tree = xml.etree.ElementTree.parse(path)
    root = tree.getroot()

    # Gets info
    info = {}
    for child in root[0]:
        info[child.tag] = child.text

    # Check if there is calibration vectors
    if root[2].tag == "calibrationVectorList":
        calvectors = root[2]
    else:
        print('No calibration list found')
        return None, info

    azimuth_time = np.array([], dtype=np.datetime64)
    line = np.array([], dtype=int)
    pixel = np.array([], dtype=int)
    sigma_0 = np.array([], dtype=float)
    beta_0 = np.array([], dtype=float)
    gamma = np.array([], dtype=float)
    dn = np.array([], dtype=float)

    for calvec in calvectors:
        azimuth_time_i = np.datetime64(calvec[0].text)
        line_i = int(calvec[1].text)
        pixel_i = np.array(list(map(int, calvec[2].text.split())))
        sigma_0_i = np.array(list(map(float, calvec[3].text.split())))
        beta_0_i = np.array(list(map(float, calvec[4].text.split())))
        gamma_i = np.array(list(map(float, calvec[5].text.split())))
        dn_i = np.array(list(map(float, calvec[6].text.split())))

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
        "abs_calibration_const": root[1][0],
        "azimuth_time": azimuth_time,
        "row": line,
        "col": pixel,
        "sigma_0": sigma_0,
        "beta_0": beta_0,
        "gamma": gamma,
        "dn": dn,
    }

    return calibration, info


#def _load_annotation(path):

#    return annotation, info