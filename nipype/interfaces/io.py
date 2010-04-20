""" Set of interfaces that allow interaction with data. Currently
    available interfaces are:

    DataSource: Generic nifti to named Nifti interface
    DataSink: Generic named output from interfaces to data store

    To come :
    XNATSource, XNATSink

"""
from copy import deepcopy
import glob
import os
import shutil

from enthought.traits.trait_errors import TraitError

from nipype.interfaces.base import Interface, CommandLine, Bunch, InterfaceResult,\
    NEW_Interface, TraitedSpec, traits, File, Directory, isdefined, BaseInterfaceInputSpec,\
    NEW_BaseInterface, OutputMultiPath, DynamicTraitedSpec, BaseTraitedSpec
from nipype.utils.filemanip import copyfile, list_to_filename, filename_to_list, FileNotFoundError

def add_traits(base, names, trait_type=None):
    """ Add traits to a traited class.

    All traits are set to Undefined by default
    """
    if trait_type is None:
        trait_type = traits.Any
    undefined_traits = {}
    for key in names:
        base.add_trait(key, trait_type)
        undefined_traits[key] = traits.Undefined
    base.trait_set(trait_change_notify=False, **undefined_traits)
    # access each trait
    for key in names:
        value = getattr(base, key)
    return base

class IOBase(NEW_BaseInterface):

    def _run_interface(self, runtime):
        runtime.returncode = 0
        return runtime

    def _list_outputs(self):
        raise NotImplementedError

    def _outputs(self):
        return self._add_output_traits(super(IOBase, self)._outputs())
    
    def _add_output_traits(self, base):
        return base
    
class DataSinkInputSpec(BaseInterfaceInputSpec):
    base_directory = Directory( 
        desc='Path to the base directory consisting of subject data.')
    container = traits.Str(desc = 'Folder within basedirectory in which to store output')
    parameterization = traits.Bool(True, usedefault=True,
                                   desc='store output in parameterized structure')
    strip_dir = Directory(desc='path to strip out of filename')
    _outputs = traits.Dict(traits.Str, value={}, usedefault=True)
    
    def __setattr__(self, key, value):
        if key not in self.copyable_trait_names():
            self._outputs[key] = value
        else:
            super(DataSinkInputSpec, self).__setattr__(key, value)
    
class DataSink(IOBase):
    """ Generic datasink module that takes a directory containing a
        list of nifti files and provides a set of structured output
        fields.
    """
    input_spec = DataSinkInputSpec

    def _get_dst(self, src):
        #print 'isrc', src
        path, fname = os.path.split(src)
        if self.inputs.parameterization:
            dst = path
            if isdefined(self.inputs.strip_dir):
                dst = dst.replace(self.inputs.strip_dir,'')
            folders = [folder for folder in dst.split(os.path.sep) if folder.startswith('_')]
            dst = os.path.sep.join(folders)
            if fname:
                dst = os.path.join(dst,fname)
        else:
            if fname:
                dst = fname
            else:
                dst = path.split(os.path.sep)[-1]
        if dst[0] == os.path.sep:
            dst = dst[1:]
        #print 'dst', dst
        return dst
        
    def _list_outputs(self):
        """Execute this module.
        """
        outdir = self.inputs.base_directory
        if not isdefined(outdir):
            outdir = '.'
        outdir = os.path.abspath(outdir)
        if isdefined(self.inputs.container):
            outdir = os.path.join(outdir, self.inputs.container)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        for key,files in self.inputs._outputs.items():
            files = filename_to_list(files)
            outfiles = []
            tempoutdir = outdir
            for d in key.split('.'):
                if d[0] == '@':
                    continue
                tempoutdir = os.path.join(tempoutdir,d)
            if not os.path.exists(tempoutdir):
                #print 'tmpoutdir', tempoutdir
                os.makedirs(tempoutdir)
            for src in filename_to_list(files):
                #print 'src',src
                src = os.path.abspath(src)
                if os.path.isfile(src):
                    dst = self._get_dst(src)
                    dst = os.path.join(tempoutdir, dst)
                    path,_ = os.path.split(dst)
                    if not os.path.exists(path):
                        #print 'path',path
                        os.makedirs(path)
                    #print 'copyfile',src, dst
                    copyfile(src, dst, copy=True)
                elif os.path.isdir(src):
                    dst = self._get_dst(os.path.join(src,''))
                    dst = os.path.join(tempoutdir, dst)
                    path,_ = os.path.split(dst)
                    if os.path.exists(path):
                        #print "removing: ", path
                        shutil.rmtree(path)
                    print "copydir", src, dst
                    shutil.copytree(src, dst)
        return None


class DataGrabberInputSpec(DynamicTraitedSpec): #InterfaceInputSpec):
    base_directory = Directory(exists=True,
            desc='Path to the base directory consisting of subject data.')
    template = traits.Str(mandatory=True,
             desc='Layout used to get files. relative to base directory if defined')
    template_args = traits.Dict(traits.Str,
                                traits.List(traits.List),
                                value=dict(outfiles=[]), usedefault=True,
                                desc='Information to plug into template')

class DataGrabber(IOBase):
    """ Generic datagrabber module that wraps around glob in an
        intelligent way for neuroimaging tasks to grab files

        Doesn't support directories currently

        Examples
        --------
        >>> from nipype.interfaces.io import DataGrabber

        Pick all files from current directory
        >>> dg = DataGrabber()
        >>> dg.inputs.template = '*'

        Pick file foo/foo.nii from current directory
        >>> dg.inputs.template = '%s/%s.nii'
        >>> dg.inputs.template_args['outfiles']=[['foo','foo']]

        Same thing but with dynamically created fields
        >>> dg = DataGrabber(infields=['arg1','arg2'])
        >>> dg.inputs.template = '%s/%s.nii'
        >>> dg.inputs.arg1 = 'foo'
        >>> dg.inputs.arg2 = 'foo'

        however this latter form can be used with iterables and iterfield in a
        pipeline.

        Dynamically created, user-defined input and output fields
        >>> dg = DataGrabber(infields=['sid'], outfields=['func','struct','ref'])
        >>> dg.inputs.base_directory = 'nipype-tutorial/data/'
        >>> dg.inputs.template = '%s/%s.nii'
        >>> dg.inputs.template_args['func'] = [['sid',['f3','f5']]]
        >>> dg.inputs.template_args['struct'] = [['sid',['struct']]]
        >>> dg.inputs.template_args['ref'] = [['sid','ref']]
        >>> dg.inputs.sid = 's1'

        Change the template only for output field struct. The rest use the
        general template
        >>> dg.inputs.field_template = dict(struct='%s/struct.nii')
        >>> dg.inputs.template_args['struct'] = [['sid']]

    """
    input_spec = DataGrabberInputSpec
    output_spec = DynamicTraitedSpec

    def __init__(self, infields=None, outfields=None, **kwargs):
        """
        Parameters
        ----------
        infields : list of str
            Indicates the input fields to be dynamically created

        outfields: list of str
            Indicates output fields to be dynamically created

        See class examples for usage
        
        """
        super(DataGrabber, self).__init__(**kwargs)
        undefined_traits = {}
        if infields:
            for key in infields:
                self.inputs.add_trait(key, traits.Any)
                undefined_traits[key] = traits.Undefined
            self.inputs.template_args['outfiles'] = [infields]
        if outfields:
            # add ability to insert field specific templates
            self.inputs.add_trait('field_template',
                                  traits.Dict(traits.Enum(outfields),
                                    desc="arguments that fit into template"))
            undefined_traits['field_template'] = traits.Undefined
            #self.inputs.remove_trait('template_args')
            outdict = {}
            for key in outfields:
                outdict[key] = []
            self.inputs.template_args =  outdict
        self.inputs.trait_set(trait_change_notify=False, **undefined_traits)

    def _add_output_traits(self, base):
        return add_traits(base, self.inputs.template_args.keys())

    def _list_outputs(self):
        outputs = {}
        for key, args in self.inputs.template_args.items():
            outputs[key] = []
            template = self.inputs.template
            if hasattr(self.inputs, 'field_template') and \
                    isdefined(self.inputs.field_template) and \
                    self.inputs.field_template.has_key(key):
                template = self.inputs.field_template[key]
            if isdefined(self.inputs.base_directory):
                template = os.path.join(os.path.abspath(self.inputs.base_directory), template)
            else:
                template = os.path.abspath(template)
            if not args:
                outputs[key] = list_to_filename(glob.glob(template))
            for argnum, arglist in enumerate(args):
                maxlen = 1
                for arg in arglist:
                    if isinstance(arg, str) and hasattr(self.inputs, arg):
                        arg = getattr(self.inputs, arg)
                    if isinstance(arg, list):
                        if (maxlen > 1) and (len(arg) != maxlen):
                            raise ValueError('incompatible number of arguments for %s' % key)
                        if len(arg)>maxlen:
                            maxlen = len(arg)
                outfiles = []
                for i in range(maxlen):
                    argtuple = []
                    for arg in arglist:
                        if isinstance(arg, str) and hasattr(self.inputs, arg):
                            arg = getattr(self.inputs, arg)
                        if isinstance(arg, list):
                            argtuple.append(arg[i])
                        else:
                            argtuple.append(arg)
                    if argtuple:
                        outfiles = list_to_filename(glob.glob(template%tuple(argtuple)))
                    else:
                        outfiles = list_to_filename(glob.glob(template))
                    outputs[key].insert(i,outfiles)
            if len(outputs[key]) == 0:
                outputs[key] = None
            elif len(outputs[key]) == 1:
                outputs[key] = outputs[key][0]
        return outputs

    def aggregate_outputs(self):
        """ Collate expected outputs and check for existence

        Overriding aggregate_outputs to modify output trait types from
        outputmultipath to either List(File) or File
        """
        
        predicted_outputs = self._list_outputs()
        outputs = self._outputs()
        if predicted_outputs:
            for key, val in predicted_outputs.items():
                outputs.remove_trait(key)
                if val is None:
                    outputs.add_trait(key, traits.Any)
                elif isinstance(val, list):
                    outputs.add_trait(key,
                                      traits.List(File(exists=True)))
                else:
                    outputs.add_trait(key, File(exists=True))
                try:
                    setattr(outputs, key, val)
                except TraitError, error:
                    if error.info == "a file name":
                        msg = "File '%s' not found for %s output '%s'." \
                            % (val, self.__class__.__name__, key)
                        raise FileNotFoundError(msg)
                    else:
                        raise error
        return outputs


class FSSourceInputSpec(BaseInterfaceInputSpec):
    subjects_dir = Directory(desc='Freesurfer subjects directory. The ' \
                                 'program will try to retrieve it from the ' \
                                 'environment if available.')
    subject_id = traits.Str(mandatory=True,
                            desc='Subject name for whom to retrieve data')
    hemi = traits.Enum('both', 'lh', 'rh', usedefault=True,
                       desc='Selects hemisphere specific outputs')

class FSSourceOutputSpec(TraitedSpec):
    T1 = File(exists=True, desc='T1 image', loc='mri')
    aseg = File(exists=True, desc='Auto-seg image', loc='mri')
    brain = File(exists=True, desc='brain only image', loc='mri')
    brainmask = File(exists=True, desc='brain binary mask', loc='mri')
    filled = File(exists=True, desc='?', loc='mri')
    norm = File(exists=True, desc='intensity normalized image', loc='mri')
    nu = File(exists=True, desc='?', loc='mri')
    orig = File(exists=True, desc='original image conformed to FS space',
                loc='mri')
    rawavg = File(exists=True, desc='averaged input images to recon-all',
                  loc='mri')
    ribbon = OutputMultiPath(File(exists=True), desc='cortical ribbon', loc='mri',
                       altkey='*ribbon')
    wm = File(exists=True, desc='white matter image', loc='mri')
    wmparc = File(exists=True, desc='white matter parcellation', loc='mri')
    curv = OutputMultiPath(File(exists=True), desc='surface curvature files',
                     loc='surf')
    inflated = OutputMultiPath(File(exists=True), desc='inflated surface meshes',
                         loc='surf')
    pial = OutputMultiPath(File(exists=True), desc='pial surface meshes', loc='surf')
    smoothwm = OutputMultiPath(File(exists=True), loc='surf',
                         desc='smooth white-matter surface meshes')
    sphere = OutputMultiPath(File(exists=True), desc='spherical surface meshes',
                       loc='surf')
    sulc = OutputMultiPath(File(exists=True), desc='surface sulci files', loc='surf')
    thickness = OutputMultiPath(File(exists=True), loc='surf',
                          desc='surface thickness files')
    volume = OutputMultiPath(File(exists=True), desc='surface volume files', loc='surf')
    white = OutputMultiPath(File(exists=True), desc='white matter surface meshes',
                      loc='surf')
    label = OutputMultiPath(File(exists=True), desc='volume and surface label files',
                      loc='label', altkey='*label')
    annot = OutputMultiPath(File(exists=True), desc='surface annotation files',
                      loc='label', altkey='*annot')
    aparc_aseg = OutputMultiPath(File(exists=True), loc='mri', altkey='aparc*aseg',
                           desc='aparc+aseg file')
    sphere_reg = OutputMultiPath(File(exists=True), loc='surf', altkey='sphere.reg',
                           desc='spherical registration file')

class FreeSurferSource(IOBase):
    """Generates freesurfer subject info from their directories

    Examples
    --------

    >>> from nipype.interfaces.io import FreeSurferSource
    >>> fs = FreeSurferSource()
    >>> #fs.inputs.subjects_dir = '/software/data/STUT/FSDATA/'
    >>> fs.inputs.subject_id = 'PWS04'
    >>> res = fs.run()

    >>> fs.inputs.hemi = 'lh'
    >>> res = fs.run()

    """
    input_spec = FSSourceInputSpec
    output_spec = FSSourceOutputSpec

    def _get_files(self, path, key, dirval, altkey=None):
        globsuffix = ''
        if dirval == 'mri':
            globsuffix = '.mgz'
        globprefix = ''
        if key == 'ribbon' or dirval in ['surf', 'label']:
            if self.inputs.hemi != 'both':
                globprefix = self.inputs.hemi+'.'
            else:
                globprefix = '*'
        keydir = os.path.join(path,dirval)
        if altkey:
            key = altkey
        globpattern = os.path.join(keydir,''.join((globprefix,key,globsuffix)))
        print globpattern
        return glob.glob(globpattern)
    
    def _list_outputs(self):
        subjects_dir = self.inputs.subjects_dir
        if not subjects_dir:
            subjects_dir = os.getenv('SUBJECTS_DIR')
        if not subjects_dir:
            raise Exception('SUBJECTS_DIR variable must be set or '\
                                'provided as input to FreeSurferSource.')
        subject_path = os.path.join(subjects_dir, self.inputs.subject_id)
        output_traits = self._outputs()
        outputs = output_traits.get()
        for k in outputs.keys():
            val = self._get_files(subject_path, k,
                                  output_traits.traits()[k].loc,
                                  output_traits.traits()[k].altkey)
            if val:
                outputs[k] = list_to_filename(val)
        return outputs
        
        
        
