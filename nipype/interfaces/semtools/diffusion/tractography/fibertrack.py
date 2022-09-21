# -*- coding: utf-8 -*-
# -*- coding: utf8 -*-
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

import os

from ....base import (
    CommandLine,
    CommandLineInputSpec,
    SEMLikeCommandLine,
    TraitedSpec,
    File,
    Directory,
    traits,
    isdefined,
    InputMultiPath,
    OutputMultiPath,
)


class fibertrackInputSpec(CommandLineInputSpec):
    input_tensor_file = File(
        desc="Tensor Image", exists=True, argstr="--input_tensor_file %s"
    )
    input_roi_file = File(
        desc="The filename of the image which contains the labels used for seeding and constraining the algorithm.",
        exists=True,
        argstr="--input_roi_file %s",
    )
    output_fiber_file = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc="The filename for the fiber file produced by the algorithm. This file must end in a .fib or .vtk extension for ITK spatial object and vtkPolyData formats respectively.",
        argstr="--output_fiber_file %s",
    )
    source_label = traits.Int(
        desc="The label of voxels in the labelfile to use for seeding tractography. One tract is seeded from the center of each voxel with this label",
        argstr="--source_label %d",
    )
    target_label = traits.Int(
        desc="The label of voxels in the labelfile used to constrain tractography. Tracts that do not pass through a voxel with this label are rejected. Set this keep all tracts.",
        argstr="--target_label %d",
    )
    forbidden_label = traits.Int(desc="Forbidden label", argstr="--forbidden_label %d")
    whole_brain = traits.Bool(
        desc="If this option is enabled all voxels in the image are used to seed tractography. When this option is enabled both source and target labels function as target labels",
        argstr="--whole_brain ",
    )
    max_angle = traits.Float(
        desc="Maximum angle of change in radians", argstr="--max_angle %f"
    )
    step_size = traits.Float(
        desc="Step size in mm for the tracking algorithm", argstr="--step_size %f"
    )
    min_fa = traits.Float(
        desc="The minimum FA threshold to continue tractography", argstr="--min_fa %f"
    )
    force = traits.Bool(desc="Ignore sanity checks.", argstr="--force ")
    verbose = traits.Bool(desc="produce verbose output", argstr="--verbose ")
    really_verbose = traits.Bool(
        desc="Follow detail of fiber tracking algorithm", argstr="--really_verbose "
    )


class fibertrackOutputSpec(TraitedSpec):
    output_fiber_file = File(
        desc="The filename for the fiber file produced by the algorithm. This file must end in a .fib or .vtk extension for ITK spatial object and vtkPolyData formats respectively.",
        exists=True,
    )


class fibertrack(SEMLikeCommandLine):
    """title: FiberTrack (DTIProcess)

    category: Diffusion.Tractography

    description: This program implements a simple streamline tractography method based on the principal eigenvector of the tensor field. A fourth order Runge-Kutta integration rule used to advance the streamlines.
    As a first parameter you have to input the tensor field (with the --input_tensor_file option). Then the region of interest image file is set with the --input_roi_file. Next you want to set the output fiber file name after the --output_fiber_file option.
    You can specify the label value in the input_roi_file with the --target_label, --source_label and  --fobidden_label options. By default target label is 1, source label is 2 and forbidden label is 0. The source label is where the streamlines are seeded, the target label defines the voxels through which the fibers must pass by to be kept in the final fiber file and the forbidden label defines the voxels where the streamlines are stopped if they pass through it. There is also a --whole_brain option which, if enabled, consider both target and source labels of the roi image as target labels and all the voxels of the image are considered as sources.
    During the tractography, the --fa_min parameter is used as the minimum value needed at different voxel for the tracking to keep going along a streamline. The --step_size parameter is used for each iteration of the tracking algorithm and defines the length of each step. The --max_angle option defines the maximum angle allowed between two successive segments along the tracked fiber.

    version: 1.1.0

    documentation-url: http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/DTIProcess

    license: Copyright (c)  Casey Goodlett. All rights reserved.
      See http://www.ia.unc.edu/dev/Copyright.htm for details.
         This software is distributed WITHOUT ANY WARRANTY; without even
         the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
         PURPOSE.  See the above copyright notices for more information.

    contributor: Casey Goodlett

    acknowledgements: Hans Johnson(1,3,4); Kent Williams(1); (1=University of Iowa Department of Psychiatry, 3=University of Iowa Department of Biomedical Engineering, 4=University of Iowa Department of Electrical and Computer Engineering) provided conversions to make DTIProcess compatible with Slicer execution, and simplified the stand-alone build requirements by removing the dependencies on boost and a fortran compiler.
    """

    input_spec = fibertrackInputSpec
    output_spec = fibertrackOutputSpec
    _cmd = " fibertrack "
    _outputs_filenames = {"output_fiber_file": "output_fiber_file.vtk"}
    _redirect_x = False
