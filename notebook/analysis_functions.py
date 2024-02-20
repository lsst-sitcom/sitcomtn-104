from astropy.io import fits
from lsst.daf import butler as dafButler
from lsst.ts.imsim.opd_metrology import OpdMetrology
from lsst.ts.imsim.utils import (
    SensorWavefrontError,
)
from lsst.ts.ofc import SensitivityMatrix
import numpy as np

def compute_zernike_estimates(collection_name, butler_root_path, butler_inst_name):
    
    # Need to redefine butler because the database changed.
    butler = dafButler.Butler(butler_root_path)

    dataset_refs = butler.registry.queryDatasets(
        datasetType="zernikeEstimateAvg", collections=[f"{collection_name}"]
    )

    # Get the map for detector Id to detector name
    camera = butler.get(
        "camera",
        {"instrument": f"LSST{butler_inst_name}"},
        collections=[f"LSST{butler_inst_name}/calib/unbounded"],
    )
    det_id_map = camera.getIdMap()
    det_name_map = camera.getNameMap()

    list_of_wf_err = []

    for dataset in dataset_refs:
        data_id = {
            "instrument": dataset.dataId["instrument"],
            "detector": dataset.dataId["detector"],
            "visit": dataset.dataId["visit"],
        }

        zer_coeff = butler.get(
            "zernikeEstimateAvg",
            dataId=data_id,
            collections=[f"{collection_name}"],
        )

        sensor_wavefront_data = SensorWavefrontError()
        sensor_name = det_id_map[dataset.dataId["detector"]].getName()
        sensor_wavefront_data.sensor_name = sensor_name
        sensor_wavefront_data.sensor_id = det_name_map[sensor_name].getId()
        sensor_wavefront_data.annular_zernike_poly = zer_coeff

        list_of_wf_err.append(sensor_wavefront_data)
    
    return list_of_wf_err

def _map_opd_to_zk(opd_file_path, rot_opd_in_deg: float, num_opd: int) -> np.ndarray:
    """Map the OPD to the basis of annular Zernike polynomial (Zk).

    OPD: optical path difference.

    Parameters
    ----------
    rot_opd_in_deg : float
        Rotate OPD in degree in the counter-clockwise direction.
    num_opd : int
        Number of OPD positions calculated.

    Returns
    -------
    numpy.ndarray
        Zk data from OPD. This is a 2D array. The row is the OPD index and
        the column is z4 to z22 in um. The order of OPD index is based on
        the file name.
    """

    # Map the OPD to the Zk basis and do the collection
    # Get the number of OPD locations by looking at length of fieldX
    num_of_zk = 19
    opd_metr = OpdMetrology()
    opd_data = np.zeros((num_opd, num_of_zk))
    for idx in range(num_opd):
        opd = fits.getdata(opd_file_path, idx)

        opd_rot = opd

        # z1 to z22 (22 terms)
        zk = opd_metr.get_zk_from_opd(opd_map=opd_rot)[0]

        # Only need to collect z4 to z22
        init_idx = 3
        opd_data[idx, :] = zk[init_idx : init_idx + num_of_zk]

    return opd_data*1e-3

def compute_sensitivity_matrix(ofc_data, sensor_names):
    field_angles = [
        ofc_data.sample_points[sensor] for sensor in sensor_names
    ]
    
    dz_sensitivity_matrix = SensitivityMatrix(ofc_data)

    # Evaluate sensitivity matrix at sensor positions
    sensitivity_matrix = dz_sensitivity_matrix.evaluate(
        field_angles, 0.0
    )

    # Select sensitivity matrix only at used zernikes
    sensitivity_matrix = sensitivity_matrix[
        :, dz_sensitivity_matrix.ofc_data.zn3_idx, :
    ]

    # Reshape sensitivity matrix to dimensions
    # (#zk * #sensors, # dofs) = (19 * #sensors, 50)
    size = sensitivity_matrix.shape[2]
    sensitivity_matrix = sensitivity_matrix.reshape((-1, size))

    # Select sensitivity matrix only at used degrees of freedom
    sensitivity_matrix = sensitivity_matrix[
        ..., dz_sensitivity_matrix.ofc_data.dof_idx
    ]

    return sensitivity_matrix