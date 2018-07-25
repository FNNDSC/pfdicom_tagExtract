# System imports
import      os
import      getpass
import      argparse
import      json
import      pprint
import      csv

# Project specific imports
import      pfmisc
from        pfmisc._colors      import  Colors
from        pfmisc              import  other
from        pfmisc              import  error

import      pudb
import      pftree
import      pfdicom

import      pylab
import      matplotlib.cm       as      cm

class pfdicom_tagExtract(pfdicom.pfdicom):
    """

    A class based on the 'pfdicom' infrastructure that extracts 
    and processes DICOM tags according to several requirements.

    Powerful output formatting, such as image conversion to jpg/png
    and generation of html reports is also supported.

    """

    def declare_selfvars(self):
        """
        A block to declare self variables
        """

        #
        # Object desc block
        #
        self.str_desc                   = ''
        self.__name__                   = "pfdicom_tagExtract"

        self.str_outputFileType         = ''

        # String representations of different outputFormats
        self.strRaw                     = ''
        self.str_json                   = ''
        self.str_dict                   = ''
        self.str_col                    = ''
        self.str_raw                    = ''

        # Image conversion
        self.b_convertToImg             = False
        self.str_outputImageFile        = ''
        self.str_imageIndex             = ''
        self.f_imageScale               = None
        self.str_interpolation          = None

        # Tags
        self.b_tagList                  = False
        self.b_tagFile                  = False
        self.str_tagList                = ''
        self.str_tagFile                = ''
        self.l_tag                      = []

        # Flags
        self.b_printToScreen            = False
        self.b_useIndexhtml             = False

        self.dp                         = None
        self.log                        = None
        self.tic_start                  = 0.0
        self.pp                         = pprint.PrettyPrinter(indent=4)
        self.verbosityLevel             = -1

    def __init__(self, *args, **kwargs):
        """
        A "base" class for all pfdicom objects. This class is typically never 
        called/used directly; derived classes are used to provide actual end
        functionality.

        This class really only reads in a DICOM file, and populates some
        internal convenience member variables.

        Furthermore, this class does not have a concept nor concern about 
        "output" relations.
        """

        def imageFileName_process(str_imageFile):
            b_OK                = False
            l_indexAndFile      = str_imageFile.split(':')
            if len(l_indexAndFile) == 1:
                b_OK            = True
                self.str_outputImageFile    = l_indexAndFile[0]
            if len(l_indexAndFile) == 2:
                b_OK            = True
                self.str_outputImageFile    = l_indexAndFile[1]
                self.str_imageIndex         = l_indexAndFile[0]
            if not b_OK:
                self.dp.qprint("Invalid image specifier.", comms = 'error')
                error.fatal(self, 'imageFileSpecFail', drawBox = True)
            if len(self.str_outputImageFile):
                self.b_convertToImg         = True

        def imageScale_process(str_imageScale):
            if len(str_imageScale):
                try:
                    str_scale, str_interpolation    = str_imageScale.split(':')
                    self.str_interpolation          = str_interpolation
                except:
                    str_scale                       = str_imageScale
                self.f_imageScale                   = float(str_scale)

        def tagList_process(str_tagList):
            self.str_tagList            = str_tagList
            if len(self.str_tagList):
                self.b_tagList          = True
                self.l_tag              = self.str_tagList.split(',')

        def tagFile_process(str_tagFile):
            self.str_tagFile            = str_tagFile
            if len(self.str_tagFile):
                self.b_tagFile          = True
                with open(self.str_tagFile) as f:
                    self.l_tag          =  [x.strip('\n') for x in f.readlines()]

        def outputFile_process(str_outputFile):
            self.str_outputFileType     = str_outputFile
            self.l_outputFileType       = self.str_outputFileType.split(',')

        # pudb.set_trace()
        self.declare_selfvars()

        # Process some of the kwargs by the base class
        super().__init__(*args, **kwargs)

        for key, value in kwargs.items():
            if key == "outputFileType":     outputFile_process(value) 
            if key == 'printToScreen':      self.b_printToScreen        = bool(value)
            if key == 'useIndexhtml':       self.b_useIndexhtml         = bool(value)
            if key == 'imageFile':          imageFileName_process(value)
            if key == 'imageScale':         imageScale_process(value)
            if key == 'tagFile':            tagFile_process(value)
            if key == 'tagList':            tagList_process(value)
            if key == 'verbosity':          self.verbosityLevel         = int(value)

        # Set logging
        self.dp                        = pfmisc.debug(    
                                            verbosity   = self.verbosityLevel,
                                            within      = self.__name__
                                            )
        self.log                       = pfmisc.Message()
        self.log.syslog(True)

    def filelist_prune(self, at_data, *args, **kwargs):
        """
        Given a list of files, select a single file for further
        analysis.

        NB: Error when no seriesFiles!
        """

        if len(self.str_extension):
            al_file = at_data[1]
            al_file = [x for x in al_file if self.str_extension in x]
        if self.b_convertToImg:
            if self.str_imageIndex == 'm':
                if len(al_file):
                    seriesFile = al_file[int(len(al_file)/2)]
                b_imageIndexed  = True
            if self.str_imageIndex == 'f':
                seriesFile = al_file[:-1]
                b_imageIndexed  = True
            if self.str_imageIndex == 'l':
                seriesFile = al_file[0]
                b_imageIndexed  = True
            if not b_imageIndexed:
                seriesFile = al_file[int(self.str_imageIndex)]
        else:
            seriesFile  = al_file[0]
        return {
            'status':   True,
            'l_file':   [seriesFile]
        }

    def inputReadCallback(self, *args, **kwargs):
        """

        Callback for reading files from specific directory.

        In the context of pfdicom_tagExtract, this implies reading
        a single DICOM file in each target directory and returning 
        the dcm data set.

        """
        b_status            = True
        str_file            = ''
        d_DCMfileRead       = {}
        filesRead           = 0

        # pudb.set_trace()

        for k, v in kwargs.items():
            if k == 'file':     str_file    = v
            if k == 'path':     str_path    = v

        if len(args):
            at_data         = args[0]
            str_path        = at_data[0]
            l_file          = at_data[1]
            str_file        = l_file[0]

        if len(str_file):
            self.dp.qprint("reading: %s/%s" % (str_path, str_file), level = 5)
            d_DCMfileRead   = self.DICOMfile_read( 
                                    file        = '%s/%s' % (str_path, str_file),
                                    l_tagsToUse = self.l_tag
            )
            b_status        = b_status and d_DCMfileRead['status']
            filesRead       += 1
        else:
            b_status        = False

        return {
            'status':           b_status,
            'str_file':         str_file,
            'str_path':         str_path,
            'd_DCMfileRead':    d_DCMfileRead,
            'filesRead':        filesRead
        }

    def inputAnalyzeCallback(self, *args, **kwargs):
        """
        Callback for doing actual work on the read data.

        The 'data' component passed to this method is the 
        dictionary returned by the inputReadCallback()
        method.

        """
        d_DCMfileRead       = {}
        b_formatted         = False

        b_rawStringAssigned = False

        # pudb.set_trace()

        for k, v in kwargs.items():
            if k == 'd_inputRead':      d_inputRead     = v
            if k == 'path':             str_path        = v

        if len(args):
            at_data         = args[0]
            str_path        = at_data[0]
            d_inputRead     = at_data[1]

        # Historically the following were member variables, but
        # due to threading concerns these were elevated to local 
        # variables to avoid scoping collisions.
        str_json        = ''
        str_dict        = ''
        str_col         = ''
        str_raw         = ''
        if 'd_DCMfileRead' in d_inputRead.keys():
            d_DCMfileRead = d_inputRead['d_DCMfileRead']

        if d_DCMfileRead:
            l_tagsToUse = d_DCMfileRead['l_tagsToUse']
            for str_outputFormat in self.l_outputFileType:
                # pudb.set_trace()
                if str_outputFormat == 'json':
                    str_json    = json.dumps(
                                        d_DCMfileRead\
                                        ['d_DICOM']\
                                        ['d_json'], 
                                        indent              = 4, 
                                        sort_keys           = True
                                    )
                    b_formatted = True
                if str_outputFormat == 'dict':
                    str_dict    = self.pp.pformat(d_DCMfileRead\
                                                    ['d_DICOM']
                                                    ['d_dicomSimple']
                                                )
                    b_formatted = True
                if str_outputFormat == 'col':
                    for tag in l_tagsToUse:
                        str_col     += '%70s\t%s\n' % ( tag, 
                                                        d_DCMfileRead\
                                                        ['d_DICOM']
                                                        ['d_dicomSimple']
                                                        [tag])
                    b_formatted     = True
                if str_outputFormat == 'raw' or str_outputFormat == 'html':
                    for tag in l_tagsToUse:
                        if not b_rawStringAssigned:
                            str_raw += '%s\n' % (d_DCMfileRead\
                                                ['d_DICOM']
                                                ['d_dicom']
                                                [tag])
                    if not b_rawStringAssigned:
                        b_rawStringAssigned      = True

        return {
            'formatted':        b_formatted,
            'd_DCMfileRead':    d_DCMfileRead,
            'dstr_result':      {
                'json':         str_json,
                'dict':         str_dict,
                'col':          str_col,
                'raw':          str_raw
            }
        }

    def img_create(self, d_DICOM, astr_path):
        '''
        Create and save an image conversion of the DICOM file.
        :return:
        '''
        # pudb.set_trace()
        b_status            = False
        d_tagsInString      = self.tagsInString_process(d_DICOM,
                                                        self.str_outputImageFile)
        str_outputImageFile = d_tagsInString['str_result']
        str_pathFile        = '%s/%s' % (astr_path, str_outputImageFile)
        self.dp.qprint('Saving image file: %s...' % str_pathFile, level = 5)
        try:
            image           = d_DICOM['dcm'].pixel_array
            pylab.imshow(image, cmap=pylab.cm.bone, interpolation = self.str_interpolation)
            ax              = pylab.gca()
            F               = pylab.gcf()
            defaultSize     = F.get_size_inches()
            if self.f_imageScale: 
                F.set_size_inches( (defaultSize[0]*self.f_imageScale, 
                                    defaultSize[1]*self.f_imageScale) )
            ax.set_facecolor('#1d1f21')
            ax.tick_params(axis = 'x', colors='white')
            ax.tick_params(axis = 'y', colors='white')
            pylab.savefig(str_pathFile, facecolor = ax.get_facecolor())
            if self.f_imageScale:
                F.set_size_inches(defaultSize)
            b_status    = True
        except:
            pass
        if not b_status:
            self.dp.qprint('Some error was trapped in image creation.',   comms = 'error')
            self.dp.qprint('path = %s' % astr_path, comms = 'error')
        return {
            'status':               b_status,
            'str_outputImageFile':  str_outputImageFile
        }

    def outputSaveCallback(self, at_data, **kwags):
        """

        Callback for saving outputs.

        In order to be thread-safe, all directory/file 
        descriptors must be *absolute* and no chdir()'s
        must ever be called!

        The input 'data' is the return dictionary from the
        inputAnalyzeCallback method.

        """
        def html_make(str_inputFile, str_rawContent, *args):
            str_img     = ""
            if self.b_convertToImg:
                str_img = "<img src=%s>" % args[0]
            htmlPage = '''
                <!DOCTYPE html>
                <html>
                <head>
                <title>DCM tags: %s</title>
                </head>
                <body style = "background-color: #1d1f21; color: white">
                %s
                <div style="text-align:left">
                    <pre>
                %s
                    </pre>
                </div>
                </body>
                </html> ''' % (str_inputFile, str_img, "\n" + str_rawContent)
            return htmlPage

        path                = at_data[0]
        d_outputInfo        = at_data[1]
        str_outputImageFile = ""
        d_convertToImg      = {}
        str_cwd             = os.getcwd()
        other.mkdir(self.str_outputDir)
        filesSaved          = 0
        other.mkdir(path)

        # pudb.set_trace()

        if self.b_printToScreen:
            print(d_outputInfo['dstr_result']['raw'])

        if self.b_convertToImg:
            d_convertToImg      = self.img_create(d_outputInfo\
                                                    ['d_DCMfileRead']
                                                    ['d_DICOM'], path)
            str_outputImageFile = d_convertToImg['str_outputImageFile']
        for str_outputFormat in self.l_outputFileType:
            str_fileStem        = d_outputInfo['d_DCMfileRead']['outputFileStem']
            if len(str_fileStem):
                if str_outputFormat == 'json': 
                    str_fileName = str_fileStem + '.json' 
                    with open('%s/%s' % (path, str_fileName), 'w') as f:
                        f.write(d_outputInfo['dstr_result']['json'])
                    self.dp.qprint('Saved report file: %s' % str_fileName, level = 5)
                    filesSaved  += 1
                if str_outputFormat == 'dict': 
                    str_fileName = str_fileStem + '-dict.txt' 
                    with open('%s/%s' % (path, str_fileName), 'w') as f:
                        f.write(d_outputInfo['dstr_result']['dict'])
                    self.dp.qprint('Saved report file: %s' % str_fileName, level = 5)
                    filesSaved  += 1
                if str_outputFormat == 'col': 
                    str_fileName = str_fileStem + '-col.txt' 
                    with open('%s/%s' % (path, str_fileName), 'w') as f:
                        f.write(d_outputInfo['dstr_result']['col'])
                    self.dp.qprint('Saved report file: %s' % str_fileName, level = 5)
                    filesSaved  += 1
                if str_outputFormat == 'raw': 
                    str_fileName = str_fileStem + '-raw.txt' 
                    with open('%s/%s' % (path, str_fileName), 'w') as f:
                        f.write(d_outputInfo['dstr_result']['raw'])
                    self.dp.qprint('Saved report file: %s' % str_fileName, level = 5)
                    filesSaved  += 1
                if str_outputFormat == 'html': 
                    str_fileName = str_fileStem + '.html'
                    if self.b_useIndexhtml:
                        str_fileName = 'index.html' 
                    with open('%s/%s' % (path, str_fileName), 'w') as f:
                        f.write(
                            html_make(  d_outputInfo['d_DCMfileRead']['inputFilename'],
                                        d_outputInfo['dstr_result']['raw'],
                                        str_outputImageFile)
                        )
                    self.dp.qprint('Saved report file: %s' % str_fileName, level = 5)
                    filesSaved  += 1
                if str_outputFormat == 'csv':
                    str_fileName = str_fileStem + '-csv.txt' 
                    with open('%s/%s' % (path, str_fileName), 'w') as f:
                        w = csv.DictWriter(f, d_outputInfo
                                                        ['d_DCMfileRead']
                                                        ['d_DICOM']
                                                        ['d_json'].keys())
                        w.writeheader()
                        w.writerow(d_outputInfo
                                                        ['d_DCMfileRead']
                                                        ['d_DICOM']
                                                        ['d_json'])
                    self.dp.qprint('Saved report file: %s' % str_fileName, level = 5)
                    filesSaved  += 1
        return {
            'status':       True,
            'filesSaved':   filesSaved
        }

    def tags_extract(self, **kwargs):
        """
        A simple "alias" for calling the pftree method.
        """
        d_tagExtract    = {}
        d_tagExtract    = self.pf_tree.tree_process(
                            inputReadCallback       = self.inputReadCallback,
                            analysisCallback        = self.inputAnalyzeCallback,
                            outputWriteCallback     = self.outputSaveCallback,
                            persistAnalysisResults  = False
        )
        return d_tagExtract

    def run(self, *args, **kwargs):
        """
        The run method is merely a thin shim down to the 
        embedded pftree run method.
        """
        b_status        = True
        d_tagExtract    = {}
        d_pftreeRun     = {}

        self.dp.qprint(
                "Starting pfdicom_tagSub run... (please be patient while running)", 
                level = 1
                )

        for k, v in kwargs.items():
            if k == 'timerStart':   other.tic()

        # Run the base class, which probes the file tree
        # and does an initial analysis. Also suppress the
        # base class from printing JSON results since those 
        # will be printed by this class
        d_pfdicom       = super().run(
                                        JSONprint   = False,
                                        timerStart  = False
                                    )

        if d_pfdicom['status']:
            str_startDir    = os.getcwd()
            os.chdir(self.str_inputDir)
            if b_status:
                d_tagExtract    = self.tags_extract()
                b_status        = b_status and d_tagExtract['status']
            os.chdir(str_startDir)

        d_ret = {
            'status':           b_status,
            'd_pfdicom':        d_pfdicom,
            'd_tagExtract':     d_tagExtract,
            'runTime':          other.toc()
        }

        if self.b_json:
            self.ret_dump(d_ret, **kwargs)

        self.dp.qprint('Returning from pfdicom_tagExtract run...', level = 1)

        return d_ret
