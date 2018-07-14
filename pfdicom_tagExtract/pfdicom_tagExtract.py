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

        # Tags
        self.b_tagList                  = False
        self.b_tagFile                  = False
        self.str_tagList                = ''
        self.str_tagFile                = ''
        self.l_tag                      = []

        # Flags
        self.b_printToScreen            = False

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
            if key == 'printToScreen':      self.b_printToScreen       = value
            if key == 'imageFile':          imageFileName_process(value)
            if key == 'tagFile':            tagFile_process(value)
            if key == 'tagList':            tagList_process(value)
            if key == 'verbosity':          self.verbosityLevel         = int(value)

        # Set logging
        self.dp                        = pfmisc.debug(    
                                            verbosity   = self.verbosityLevel,
                                            level       = 0,
                                            within      = self.__name__
                                            )
        self.log                       = pfmisc.Message()
        self.log.syslog(True)

    def filelist_prune(self, at_data, *args, **kwargs):
        """
        Given a list of files, select a single file for further
        analysis.
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

    def tags_process(self, *args, **kwargs):
        """
        Process the tag information for given file and
        create string representations of various required
        output formats.
        """

        str_file            = ''
        str_result          = ''
        b_formatted         = False
        str_outputFile      = ''

        self.dcm            = None
        self.d_dcm          = {}
        self.d_dicom        = {}
        self.d_dicomSimple  = {}

        b_rawStringAssigned = False

        for k, v in kwargs.items():
            if k == 'file':     str_file    = v

        if len(args):
            at_data         = args[0]
            str_path        = at_data[0]
            l_file          = at_data[1]
            str_file        = l_file[0]

        self.str_json       = ''
        self.str_dict       = ''
        self.str_col        = ''
        self.str_raw        = ''
        l_tagsToUse         = [] 
        if len(str_file):
            if self.b_tagFile or self.b_tagList:
                l_tagsToUse     = self.l_tag

            d_DCMfileRead   = self.DICOMfile_read( 
                                    file        = '%s/%s' % (str_path, str_file),
                                    l_tagsToUse = l_file
            )
            l_tagsToUse     = d_DCMfileRead['l_tagsToUse']      

            for str_outputFormat in self.l_outputFileType:
                # pudb.set_trace()
                if str_outputFormat == 'json':
                    self.str_json           = json.dumps(
                                                d_DCMfileRead['d_dicomJSON'], 
                                                indent              = 4, 
                                                sort_keys           = True
                                                )
                    b_formatted     = True
                if str_outputFormat == 'dict':
                    self.str_dict           = self.pp.pformat(self.d_dicomSimple)
                    b_formatted     = True
                if str_outputFormat == 'col':
                    for tag in l_tagsToUse:
                        self.str_col        += '%70s\t%s\n' % (tag , self.d_dicomSimple[tag])
                    b_formatted     = True
                if str_outputFormat == 'raw' or str_outputFormat == 'html':
                    for tag in l_tagsToUse:
                        if not b_rawStringAssigned:
                            self.str_raw        += '%s\n' % (self.d_dicom[tag])
                    if not b_rawStringAssigned:
                        b_rawStringAssigned      = True

        return {
            'formatted':        b_formatted,
            'd_dicom':          self.d_dicom,
            'd_dicomSimple':    self.d_dicomSimple,
            'd_dicomJSON':      d_DCMfileRead['d_dicomJSON'],
            'dcm':              self.dcm,
            'str_path':         d_DCMfileRead['inputPath'],
            'str_outputFile':   d_DCMfileRead['outputFileStem'],
            'str_inputFile':    d_DCMfileRead['inputFilename'],
            'dstr_result':      {
                'json':         self.str_json,
                'dict':         self.str_dict,
                'col':          self.str_col,
                'raw':          self.str_raw
            }
        }

    def img_create(self, dcm, astr_path):
        '''
        Create and save an image conversion of the DICOM file.
        :return:
        '''
        # pudb.set_trace()
        b_status            = False
        d_tagsInString      = self.tagsInString_process(self.str_outputImageFile)
        str_outputImageFile = d_tagsInString['str_result']
        # self.dp.qprint('Saving image file: %s...' % str_outputImageFile)
        try:
            pylab.imshow(dcm.pixel_array, cmap=pylab.cm.bone)
            ax  = pylab.gca()
            ax.set_facecolor('#1d1f21')
            ax.tick_params(axis = 'x', colors='white')
            ax.tick_params(axis = 'y', colors='white')
            pylab.savefig(str_outputImageFile, facecolor = ax.get_facecolor())
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

    def outputSave(self, at_data, **kwags):
        """
        Callback for saving outputs.
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
                    <pre>
                %s
                    </pre>
                </body>
                </html> ''' % (str_inputFile, str_img, "\n" + str_rawContent)
            return htmlPage

        d_outputInfo        = at_data[1]
        str_outputImageFile = ""
        d_convertToImg      = {}
        path                = d_outputInfo['str_path']
        str_cwd             = os.getcwd()
        other.mkdir(self.str_outputDir)
        # self.dp.qprint("In output base directory:     %s" % self.str_outputDir)
        # self.dp.qprint("Generating report for record: %s" % path)
        os.chdir(self.str_outputDir)
        other.mkdir(path)
        os.chdir(path)
        if self.b_printToScreen:
            print(d_outputInfo['dstr_result']['raw'])
        if self.b_convertToImg:
            d_convertToImg      = self.img_create(d_outputInfo['dcm'], path)
            str_outputImageFile = d_convertToImg['str_outputImageFile']
        for str_outputFormat in self.l_outputFileType:
            if str_outputFormat == 'json': 
                str_fileName = d_outputInfo['str_outputFile']+'.json' 
                with open(str_fileName, 'w') as f:
                    f.write(d_outputInfo['dstr_result']['json'])
                # self.dp.qprint('Saved report file: %s' % str_fileName)
            if str_outputFormat == 'dict': 
                str_fileName = d_outputInfo['str_outputFile']+'-dict.txt' 
                with open(str_fileName, 'w') as f:
                    f.write(d_outputInfo['dstr_result']['dict'])
                # self.dp.qprint('Saved report file: %s' % str_fileName)
            if str_outputFormat == 'col': 
                str_fileName = d_outputInfo['str_outputFile']+'-col.txt' 
                with open(str_fileName, 'w') as f:
                    f.write(d_outputInfo['dstr_result']['col'])
                # self.dp.qprint('Saved report file: %s' % str_fileName)
            if str_outputFormat == 'raw': 
                str_fileName = d_outputInfo['str_outputFile']+'-raw.txt' 
                with open(str_fileName, 'w') as f:
                    f.write(d_outputInfo['dstr_result']['raw'])
                # self.dp.qprint('Saved report file: %s' % str_fileName)
            if str_outputFormat == 'html': 
                str_fileName = d_outputInfo['str_outputFile']+'.html' 
                with open(str_fileName, 'w') as f:
                    f.write(
                        html_make(  d_outputInfo['str_inputFile'],
                                    d_outputInfo['dstr_result']['raw'],
                                    str_outputImageFile)
                    )
                # self.dp.qprint('Saved report file: %s' % str_fileName)
            if str_outputFormat == 'csv':
                str_fileName = d_outputInfo['str_outputFile']+'-csv.txt' 
                with open(str_fileName, 'w') as f:
                    w = csv.DictWriter(f, d_outputInfo['d_dicomJSON'].keys())
                    w.writeheader()
                    w.writerow(d_outputInfo['d_dicomJSON'])
                # self.dp.qprint('Saved report file: %s' % str_fileName)
        os.chdir(str_cwd)
        return {
            'status':   True
        }

    def run(self, *args, **kwargs):
        """
        The run method is merely a thin shim down to the 
        embedded pftree run method.
        """
        b_status    = True
        d_pftreeRun = {}

        d_env       = self.env_check()
        if d_env['status']:
            d_pftreeRun = self.pf_tree.run()
        else:
            b_status    = False 

        str_startDir    = os.getcwd()
        os.chdir(self.str_inputDir)
        if b_status:
            d_inputAnalysis = self.pf_tree.tree_analysisApply(
                                analysiscallback        = self.filelist_prune,
                                applyResultsTo          = 'inputTree',
                                applyKey                = 'l_file',
                                persistAnalysisResults  = True
            )
            d_tagsExtract   = self.pf_tree.tree_analysisApply(
                                analysiscallback        = self.tags_process,
                                outputcallback          = self.outputSave,
                                persistAnalysisResults  = False
            )

        os.chdir(str_startDir)
        return {
            'status':       b_status and d_pftreeRun['status'],
            'd_env':        d_env,
            'd_pftreeRun':  d_pftreeRun
        }
        