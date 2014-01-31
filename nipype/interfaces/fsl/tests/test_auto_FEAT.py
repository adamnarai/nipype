# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from nipype.testing import assert_equal
from nipype.interfaces.fsl.model import FEAT

def test_FEAT_inputs():
    input_map = dict(args=dict(argstr='%s',
    ),
    environ=dict(nohash=True,
    usedefault=True,
    ),
    fsf_file=dict(argstr='%s',
    mandatory=True,
    position=0,
    ),
    ignore_exception=dict(nohash=True,
    usedefault=True,
    ),
    output_type=dict(),
    terminal_output=dict(mandatory=True,
    nohash=True,
    ),
    )
    inputs = FEAT.input_spec()

    for key, metadata in input_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(inputs.traits()[key], metakey), value

def test_FEAT_outputs():
    output_map = dict(feat_dir=dict(),
    )
    outputs = FEAT.output_spec()

    for key, metadata in output_map.items():
        for metakey, value in metadata.items():
            yield assert_equal, getattr(outputs.traits()[key], metakey), value
