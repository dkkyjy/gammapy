# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
from scipy.sparse import csr_matrix
from astropy.io import fits
from astropy.coordinates import SkyCoord
from .geom import MapCoords, val_to_bin, pix_tuple_to_idx
from .hpxmap import HpxMap
from .hpx import HPXGeom, HpxToWcsMapping, ravel_hpx_index, unravel_hpx_index

__all__ = [
    'HpxMapSparse',
]


class HpxMapSparse(HpxMap):
    """Representation of a N+2D map using HEALPIX with two spatial
    dimensions and N non-spatial dimensions.

    This class uses a sparse matrix for HEALPix pixel values.

    Parameters
    ----------
    hpx : `~gammapy.maps.hpx.HPXGeom`
        HEALPIX geometry object.
    data : `~numpy.ndarray`
        HEALPIX data array.

    """

    def __init__(self, hpx, data=None):

        shape = (1, np.sum(hpx.npix),)

        # TODO : accept sparse matrix for data argument
        if data is None:
            data = csr_matrix(shape)
        else:
            data = csr_matrix(np.ravel(data).reshape((1, -1)))

        HpxMap.__init__(self, hpx, data)

    def get_by_coords(self, coords, interp=None):

        if interp is None:
            pix = self.hpx.coord_to_pix(coords)
            return self.get_by_pix(pix)
        else:
            raise NotImplementedError

    def get_by_pix(self, pix, interp=None):

        if interp is None:
            # Convert to local pixel indices
            idx = pix_tuple_to_idx(pix)
            idx = self.hpx.global_to_local(idx)
            idx = ravel_hpx_index(idx, self.hpx.npix)
            return np.array(self.data[0, idx])
        else:
            raise NotImplementedError

    def fill_by_coords(self, coords, weights=None):

        pix = self.geom.coord_to_pix(coords)
        self.fill_by_pix(pix, weights)

    def fill_by_pix(self, pix, weights=None):

        idx = pix_tuple_to_idx(pix)
        if weights is None:
            weights = np.ones(idx[0].shape)
        idx = self.hpx.global_to_local(idx)
        idx = ravel_hpx_index(idx, self.hpx.npix)
        self.data[0, idx] += weights

    def set_by_coords(self, coords, vals):

        pix = self.geom.coord_to_pix(coords)
        self.set_by_pix(pix, vals)

    def set_by_pix(self, pix, vals):

        idx = pix_tuple_to_idx(pix)
        idx = self.hpx.global_to_local(idx)
        idx = ravel_hpx_index(idx, self.hpx.npix)
        self.data[0, idx] = vals

    def sum_over_axes(self):
        raise NotImplementedError

    def to_wcs(self, sum_bands=False, normalize=True, proj='AIT', oversample=2):
        raise NotImplementedError

    def to_swapped_scheme(self):
        raise NotImplementedError

    def to_ud_graded(self):
        raise NotImplementedError
