# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from nipype.testing import assert_equal
from nipype.algorithms.misc import Overlap

def test_Overlap_inputs():
    input_map = dict(ignore_exception=dict(nohash=True,
    usedefault=True,
    ),
    mask_volume=dict(),
    out_file=dict(usedefault=True,
    ),
    volume1=dict(mandatory=True,
    ),
    volume2=dict(mandatory=True,
    ),
    )
    inputs = Overlap.input_spec()

    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(inputs.traits()[key], metakey), value

def test_Overlap_outputs():
    output_map = dict(dice=dict(),
    diff_file=dict(),
    jaccard=dict(),
    volume_difference=dict(),
    )
    outputs = Overlap.output_spec()

    for key, metadata in output_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(outputs.traits()[key], metakey), value
