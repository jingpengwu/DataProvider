from __future__ import print_function
import math

from . import blend
from ..box import centered_box
from ..vector import Vec3d
from ..offset_array import OffsetArray
from cloudvolume.lib import Bbox


class ForwardScanner(object):
    """
    ForwardScanner.

    Attributes:
        dataset:
        scan_spec:
        params:
    """

    def __init__(self, dataset, scan_spec, params=None):
        """
        Initialize ForwardScanner.
        args:
            dataset (WritableTensorData or WritableTensorDataWithMask)
            scan_spec (dict(output_key=patch_size)): \
                dict(affinity=(3,18,256,256))
            params (dict): other parameters
        """
        self._init()

        self.dataset   = dataset
        self.scan_spec = scan_spec
        self.params    = params if params is not None else dict()

        self._setup()

    def pull(self):
        """
        TODO(kisuk): Documentation.
        """
        ret = None
        if self.counter < len(self.locs):
            assert self.current is None
            idx = self.counter
            loc = self.locs[idx]
            print('({}/{}) loc: {}'.format(idx+1, len(self.locs), tuple(loc)))
            ret = self.dataset.get_sample(loc)
            self.current = loc
            self.counter += 1
        return ret

    def push(self, sample):
        """
        TODO(kisuk): Documentation

        Args:
            sample:
            kwargs:
        """
        assert self.current is not None
        self.outputs.push(self.current, sample)
        self.current = None

    def voxels(self):
        return self.outputs.voxels()

    ####################################################################
    ## Private Methods.
    ####################################################################

    def _init(self):
        """Initialize all attributes."""
        self.dataset        = None
        self.scan_spec      = dict()
        self.params         = dict()
        self.offset         = (0,0,0)
        self.stride         = (0,0,0)
        self.grid           = (0,0,0)
        self.vmin           = None
        self.vmax           = None
        self.default_stride = None
        self.coords         = [None]*3
        self.locs           = None
        self.counter        = 0
        self.current        = None
        self.outputs        = None

    def _setup(self):
        """
        TODO(kisuk): Documentation.
        """
        self.offset = Vec3d(self.params.get('offset', (0,0,0)))
        self.stride = Vec3d(self.params.get('stride', (0,0,0)))
        self.grid   = Vec3d(self.params.get('grid',   (0,0,0)))

        # TODO(kisuk): Validity check?

        self.vmin = self.dataset.get_range().min() + self.offset
        self.vmax = self.dataset.get_range().max()

        # TODO(kisuk): Validity check?

        # Order is important!
        self._setup_stride()
        self._setup_coords()
        self._prepare_outputs()

    def _setup_stride(self):
        """
        TODO(kisuk): Documentation.
        """
        stride = None
        for k, v in self.scan_spec.items():
            box = centered_box(Vec3d(0,0,0), v[-3:])
            if stride is None:
                stride = box
            else:
                stride = stride.intersect(box)
        self.default_stride = stride.size()

    def _setup_coords(self):
        """
        TODO(kisuk): Documentation.
        """
        self._setup_coord(0)  # z-dimension
        self._setup_coord(1)  # y-dimension
        self._setup_coord(2)  # x-dimension

        self.locs = list()
        for z in self.coords[0]:
            for y in self.coords[1]:
                for x in self.coords[2]:
                    self.locs.append(Vec3d(z,y,x))

    def _setup_coord(self, dim):
        """
        TODO(kisuk): Documenatation.

        Args:
            dim: 0: z-dimension.
                 1: y-dimension.
                 2: x-dimension.
        """
        assert dim < 3

        # min & max coordinates.
        cmin = int(self.vmin[dim])
        cmax = int(self.vmax[dim])
        assert cmin < cmax

        # Dimension-specific params.
        stride = self.stride[dim]
        grid   = int(self.grid[dim])
        coord  = set()

        # Non-overlapping stride.
        if stride == 0:
            stride = self.default_stride[dim]
        # Overlapping stride given by an overlapping ratio.
        elif stride > 0 and stride < 1:
            stride = math.round(stride * self.default_stride[dim])
        self.stride[dim] = int(stride)
        stride = self.stride[dim]

        # Automatic full spanning.
        if grid == 0:
            grid = (cmax - cmin - 1)//stride + 1
            coord.add(cmax-1)  # Offcut

        # Scan coordinates.
        for i in range(grid):
            c = cmin + i*stride
            if c >= cmax:
                break
            coord.add(c)

        # Sanity check.
        assert cmin+(grid-1)*stride < cmax

        # Sort coords.
        self.coords[dim] = sorted(coord)

    def _prepare_outputs(self):
        """Prepare outputs according to the blending mode."""
        # Inference with overlapping window.
        diff = self.stride - self.default_stride
        overlap = True if diff[0]<0 or diff[1]<0 or diff[2]<0 else False
        # Prepare outputs.
        blend_mode = self.params.get('blend', '')
        self.outputs = blend.prepare_outputs(self.scan_spec, self.locs,
                                             blend=overlap,
                                             blend_mode=blend_mode,
                                             stride=self.stride)


class AlignedPatchForwardScanner(object):
    """
    forward pass for aligned patches
    """
    def __init__(self, output_buffer, scan_spec, output_bbox, params=None):
        """
        args:
            output_buffer (OffsetArray)
        """
        assert isinstance(buffer_chunk, OffsetArray)

    def pull(self):
        """
        TODO(kisuk): Documentation.
        """
        ret = None
        if self.counter < len(self.locs):
            assert self.current is None
            idx = self.counter
            loc = self.locs[idx]
            print('({}/{}) loc: {}'.format(idx+1, len(self.locs), tuple(loc)))
            ret = self.dataset.get_sample(loc)
            self.current = loc
            self.counter += 1
        return ret

    def push(self, sample):
        """
        TODO(kisuk): Documentation

        Args:
            sample:
            kwargs:
        """
        assert self.current is not None
        self.outputs.push(self.current, sample)
        self.current = None



