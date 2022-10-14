#!/usr/bin/env python3
#
# (c) 2017+ Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import sys, os
# sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../pfdicom_tagExtract'))

try:
    from    .               import pfdicom_tagExtract
    from    .               import __pkg, __version__
except:
    from pfdicom_tagExtract import pfdicom_tagExtract
    from __init__           import __pkg, __version__


from    argparse            import RawTextHelpFormatter
from    argparse            import ArgumentParser
import  pudb

import  pfmisc
from    pfmisc._colors      import Colors
from    pfmisc              import other

import  pfdicom
from    pfdicom.__main__    import package_CLIfull as pfdicom_CLIfull
from    pfdicom.__main__    import package_argsSynopsisFull as pfdicom_argSynopsis
from    pfdicom.__main__    import parser as pfdicom_parser

str_desc = Colors.CYAN + """


        __    _ _                      _              _____     _                  _
       / _|  | (_)                    | |            |  ___|   | |                | |
 _ __ | |_ __| |_  ___ ___  _ __ ___  | |_ __ _  __ _| |____  _| |_ _ __ __ _  ___| |_
| '_ \|  _/ _` | |/ __/ _ \| '_ ` _ \ | __/ _` |/ _` |  __\ \/ / __| '__/ _` |/ __| __|
| |_) | || (_| | | (_| (_) | | | | | || || (_| | (_| | |___>  <| |_| | | (_| | (__| |_
| .__/|_| \__,_|_|\___\___/|_| |_| |_| \__\__,_|\__, \____/_/\_\\__|_|  \__,_|\___|\__|
| |                                ______        __/ |
|_|                               |______|      |___/


                        Path-File DICOM tag extactor

        Recursively walk down a directory tree and extract DICOM tags,
        writing report files preserving directory structure in output tree.

                             -- version """ + \
             Colors.YELLOW + __version__ + Colors.CYAN + """ --

        'pfdicom_tagExtract' is a customizable and friendly DICOM tag extractor.
        As part of the "pf*" suite of applications, it is geared to IO as
        directories. Input DICOM trees are reconstructed in an output
        directory, preserving directory structure. Each node tree contains
        report files on the corresponding input location's DICOM files.


""" + Colors.NO_COLOUR

package_CLIself = '''
        [--printToScreen]                                                       \\
        [--tagFile <tagFile>] |                                                 \\
        [--tagList <tagList>] |                                                 \\
        [--raw <rawTag>]                                                        \\
        [--image <imageFile>]                                                   \\
        [--imageScale <factor>[:<interpolation>]]                               \\
        [--outputFileType <outputFileType>                                      \\
        [--useIndexhtml]                                                        \\'''

package_argSynopsisSelf = """
        [-p|--printToScreen]
        If specified, will print tags to screen.

        [--tagFile <tagFile>]
        Read the tags, one-per-line in <tagFile>, and print the
        corresponding tag information in the DICOM <inputFile>.

        [--tagList <tagList>]
        Read the list of comma-separated tags in <tagList>, and print the
        corresponding tag information parsed from the DICOM <inputFile>.

        [--image <[<index>:]imageFile>]
        If specified, also convert the <inputFile> to <imageFile>. If the
        name is preceded by an index and colon, then convert this indexed
        file in the particular <inputDir>.

        [--imageScale <factor>[:<interpolation>]]
        If an image conversion is specified, this flag will scale the image
        by <factor> and use an interpolation <order>. This is useful in
        increasing the size of images for the html output.

        Note that certain interpolation choices can result in a significant
        slowdown!

            interpolation order:

            'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'

        [--outputFileType <outputFileType>]
        A comma specified list of output types. These can be:

            o <type>    <ext>       <desc>
            o raw       -raw.txt    the raw internal dcm structure to string
            o json      .json       a json representation
            o html      .html       an html representation with optional image
            o dict      -dict.txt   a python dictionary
            o col       -col.txt    a two-column text representation (tab sep)
            o csv       .csv        a csv representation

        Note that if not specified, a default type of 'raw' is assigned.

        [--useIndexhtml]
        If specified, force the name of any output html reports to be
        'index.html'.

"""

package_CLIfull             = pfdicom_CLIfull     + package_CLIself
package_argsSynopsisFull    = pfdicom_argSynopsis + package_argSynopsisSelf

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    NAME

        pfdicom_tagExtract
        - process DICOM file header information down a file system tree.

    SYNOPSIS

            pfdicom_tagExtract \ ''' + package_CLIfull + '''                                      \\

    BRIEF EXAMPLE

        pfdicom_tagExtract                                                      \\
                --inputDir /var/www/html/normsmall                              \\
                --fileFilter dcm                                                \\
                --outputDir /var/www/html/tag                                   \\
                --outputFileStem '%_md5|6_PatientID-%PatientAge'                \\
                --imageFile 'm:%_md5|6_PatientID-%PatientAge.jpg'               \\
                --outputFileType raw,json,html,dict,col,csv                     \\
                --threads 0 --verbosity 1

    '''

    description =  '''
    DESCRIPTION

        `pfdicom_tagExtract` extracts the header information of DICOM files
        and echoes to stdout as well as to an output report-type file -- this
        can be a raw output, a json-type output, or html-type output.

        The script accepts an <inputDir>, and then from this point an os.walk
        is performed to extract all the subdirs. Each subdir is examined for
        DICOM files (in the simplest sense by a file extension mapping) and
        either the head, tail, middle (or other indexed) file is examined for
        its tag information.

        Optionally, the tag list can be constrained either by passing a
        <tagFile> containing a line-by-line list of tags to query, or
        by passing a comma separated list of tags directly.

        Finally, an image conversion can also be performed (and embedded
        within the output html file, if an html conversion is specified).

    ARGS ''' + package_argsSynopsisFull + '''

    EXAMPLES

    Extract DICOM header info down an input tree and save reports
    to output tree:

        pfdicom_tagExtract                                                      \\
                --inputDir /var/www/html/normsmall                              \\
                --fileFilter dcm                                                \\
                --outputDir /var/www/html/tag                                   \\
                --outputFileStem '%_md5|6_PatientID-%PatientAge'                \\
                --imageFile 'm:%_md5|6_PatientID-%PatientAge.jpg'               \\
                --outputFileType raw,json,html,dict,col,csv                     \\
                --imageScale 3:none                                             \\
                --useIndexhtml                                                  \\
                --outputFileType raw,json,html,dict,col,csv                     \\
                --threads 0 --verbosity 1

    will process only the "middle" DICOM file (dcm) in each series directory
    down the tree /var/www/html/normsmall, producing a jpg image of the DICOM
    as well as a series of output report formats with progressive results
    shown in the terminal. Use a --json flag to get only JSON results.

    The script can also be instructed to not process files into outputs, but to
    only print the DICOM tag information to screen of a given DICOM file
    <DCMfile>:

        pfdicom_tagExtract                                                      \\
            --verbosity 0 --inputDir ./  --printToScreen                        \\
            --inputFile <DCMfile>

    '''
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description


parserSelf  = ArgumentParser(description        = 'Self specific',
                             formatter_class    = RawTextHelpFormatter,
                             add_help           = False)

parserSelf.add_argument("--tagFile",
                    help    = "file containing tags to parse",
                    dest    = 'tagFile',
                    default = '')
parserSelf.add_argument("--tagList",
                    help    = "comma-separated tag list",
                    dest    = 'tagList',
                    default = '')
parserSelf.add_argument("--raw",
                    help    = "display raw tags",
                    dest    = 'rawType',
                    default = 'raw')
parserSelf.add_argument("--imageFile",
                    help    = "image file to convert DICOM input",
                    dest    = 'imageFile',
                    default = '')
parserSelf.add_argument("--imageScale",
                    help    = "scale images with factor and optional :interpolation",
                    dest    = 'imageScale',
                    default = '')
parserSelf.add_argument("--outputFileType",
                    help    = "list of output report types",
                    dest    = 'outputFileType',
                    default = 'raw')
parserSelf.add_argument("--useIndexhtml",
                    help    = "force html file to be called 'index.html'",
                    dest    = 'useIndexhtml',
                    action  = 'store_true',
                    default = False)
parserSelf.add_argument("--printToScreen",
                    help    = "print output to screen",
                    dest    = 'printToScreen',
                    action  = 'store_true',
                    default = False)

def earlyExit_check(args) -> int:
    """Perform some preliminary checks
    """
    if args.man or args.synopsis:
        print(str_desc)
        if args.man:
            str_help     = synopsis(False)
        else:
            str_help     = synopsis(True)
        print(str_help)
        return 1
    if args.b_version:
        print("Name:    %s\nVersion: %s" % (__pkg.name, __version__))
        return 1
    return 0

def main(argv=None):

    d_pfdicom_tagExtract    : dict  = {}

    parser  = ArgumentParser(description        = str_desc,
                             formatter_class    = RawTextHelpFormatter,
                             parents            = [pfdicom_parser, parserSelf],
                             add_help           = False)

    args = parser.parse_args()

    if earlyExit_check(args): return 1

    args.str_version        = __version__
    args.str_desc           = synopsis(True)
    pf_dicom_tagExtract     = pfdicom_tagExtract.pfdicom_tagExtract(vars(args))
    # And now run it!
    d_pfdicom_tagExtract    = pf_dicom_tagExtract.run(timerStart = True)

    if args.printElapsedTime:
        pf_dicom_tagExtract.dp.qprint(
                                    "Elapsed time = %f seconds" %
                                    d_pfdicom_tagExtract['runTime']
                                )

    return 0

if __name__ == "__main__":
    sys.exit(main())
