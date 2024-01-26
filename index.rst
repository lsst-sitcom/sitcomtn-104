:tocdepth: 1

.. sectnum::

.. Metadata such as the title, authors, and description are set in metadata.yaml

.. TODO: Delete the note below before merging new content to the main branch.

.. note::

   **This technote is a work-in-progress.**

Abstract
========

This technote covers `WET-001 Test <https://jira.lsstcorp.org/browse/SITCOM-826>`__ from the AOS Commissioning Test List. It aims to validate that the AOS is able to retrieve the optical state injected into the system.
This technote will eventually cover multiple different conditions (different filters, different rotation angles). For now, it only covers the case of the r-band filter and the 0 degree camera rotation angle.

The notebook used to generate the data for this technote can be found in `this technote repository <https://github.com/lsst-sitcom/sitcomtn-104>`__.

Background
==============

For that process to be successful the AOS relies in two different components:

1. **Wavefront Estimation Pipeline algorithm**: 
   
   The errors in estimating the wavefront zernikes influence the accuracy of the retrieved optical state. This process is also studied in other tehcnotes. The three approaches that can be considered when estimating the wavefront are:

   a. **Danish**

   b. **TIE**
   
   c. **ML**



2. **Optical state estimation**: 
   
   Once the wavefront is estimated, the optical state is retrieved through the sensitivity matrix. The process involves the pseudo-inverse of the sensitivity matrix (:math:`A`) and the truncation on those degenerate degrees of freedom.
   
   For reference, we include the main equation involved in this process. Here, :math:`y` is the estimated zernikes minus the intrinisic zernikes in microns, and :math:`x` is the retrieved optical state in the basis of degrees of freedom (microns or arcsec, depending on the degre e of freedom).
   Finally, rcond refers to the threshold used to truncate the singular values of the degrees of freedom.

   .. code::

      x = pinv(A, rcond=1e-4) @ y


Simulation
==============

For a set of 100 different optical states (degree of freedom states) we generate the corner sensor images. The optical states are generated following the process described in :cite:`Crenshaw2023AI`. 
Below two images are shown, one for the injected degree of freedom state, and one for the simulated corner image:

.. figure:: /_static/simulation.png
    :name: Simulation Image
    :target: ../_images/simulation.png
    :alt: Simulated image in corner R00 sensor for the first optical state.
    :width: 70%
    :align: center

    *Figure 1: Simulated image in corner R00 sensor for the first optical state.*


.. figure:: /_static/dofstate1.png
    :name: Optical state 1
    :align: center
    :target: ../_images/simulation.png
    :alt: First optical state of the 100 simulated states.
    :width: 50%

    *Figure 2: First optical state of the 100 simulated states.*

The images were simulated with the following conditions:

+--------------+--------------+--------------+
|     RA       |     Dec      |   Seeing     |
+==============+==============+==============+
| 15:17:00.75  | -9:22:57.7   |  0.8 arcsec  |
+--------------+--------------+--------------+

The images can currently be found in the personal butler of the author (/sdf/data/rubin/user/gmegias/projects/commissioning_sims/butler_wet001). Once the technote has been peer-reviewed and the data is vetted, it will be transferred to the AOS commissioning shared butler.

Results
================

Wavefront estimation
--------------------
So far we focus on running the WEP pipeline using the baseline TIE algorithm. The results shown below include the cutout donuts and estimated zernikes versus true zernikes for the first optical state.

.. figure:: /_static/donutstamps.png
    :name: Cutout donuts
    :target: ../_images/donutstamps.png
    :alt: Cutout donuts for the first optical state.
    :width: 50%
    :align: center

    *Figure 3: Cutout donuts for the first optical state.*

.. figure:: /_static/zernikes.png
    :name: Zernikes
    :target: ../_images/zernikes.png
    :alt: Estimated zernikes versus true zernikes for the first optical state.
    :align: center
   
    *Figure 4: Estimated zernikes versus true zernikes for the first optical state.*

Finally, we also include the median error and std of the estimated zernikes error for the 100 different optical states. The results are shown in the plot below:

.. figure:: /_static/zernike_comparison.png
    :name: Estimated zernikes error statistics
    :target: ../_images/zernike_comparison.png
    :alt: Estimated zernikes error statistics
    :width: 90%
    :align: center

    *Figure 5: Estimated zernikes error statistics*


Optical state estimation
------------------------
Finally, keeping in mind that as shown above our estimates of the wavefront are not perfect, we proceed to retrieve the optical state for the 100 different optical states. The results for the first simulated optical state are shown below. 
We include a comparison between the injected optical state versus the retrieved one, as well as comparison of the reconstructed zernikes (obtained multipliying the sensitivity matrix by the estimated optical state) versus the true zernikes and the WEP estimated ones.

.. figure:: /_static/optical_state.png
    :name: Optical state
    :target: ../_images/optical_state.png
    :alt: Injected optical state versus retrieved optical state for the first simulated optical state.
    :width: 80%
    :align: center

    *Figure 6: Injected optical state versus retrieved optical state for the first simulated optical state.*

.. figure:: /_static/zernikes_reconstructed.png
    :name: Zernikes reconstructed
    :target: ../_images/zernikes_reconstructed.png
    :alt: Reconstructed zernikes versus true zernikes and estimated zernikes for the first simulated optical state.
    :align: center

    *Figure 7: Reconstructed zernikes versus true zernikes and estimated zernikes for the first simulated optical state.*
   
Finally, we also include the median error and std of the reconstructed zernikes versus the estimated WEP zernikes. The results are shown in the plot below:

.. figure:: /_static/zernike_comparison_reconstructed.png
    :name: Reconstructed zernikes error statistics
    :target: ../_images/zernike_comparison_reconstructed.png
    :alt: Reconstructed zernike vs WEP zernike error statistics
    :align: center

    *Figure 8: Reconstructed zernike vs WEP zernike error statistics.*



.. rubric:: References

.. Make in-text citations with: :cite:`bibkey`.

.. bibliography:: local.bib lsstbib/books.bib lsstbib/lsst.bib lsstbib/lsst-dm.bib lsstbib/refs.bib lsstbib/refs_ads.bib
   :style: lsst_aa


.. raw:: html

   <style>
   .align-center {
       text-align: center;
   }
   </style>