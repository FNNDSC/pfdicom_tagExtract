pfdicom_tagExtract
==================

.. image:: https://badge.fury.io/py/pfdicom_tagExtract.svg
    :target: https://badge.fury.io/py/pfdicom_tagExtract

.. image:: https://travis-ci.org/FNNDSC/pfdicom_tagExtract.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/pfdicom_tagExtract

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/pfdicom_tagExtract

.. contents:: Table of Contents


Quick Overview
--------------

-  ``pfdicom_tagExtract`` generates reports in various formats (txt, html, etc) based on parsing DICOM meta data (i.e. DICOM tags).

Overview
--------

``pfdicom_tagExtract`` extracts the header information of DICOM files and echoes to stdout as well as to an output report-type file -- this can be a raw output, a json-type output, or html-type output.

The script accepts an ``<inputDir>``, and then from this point a recursive ``os.walk()``  is performed to probe all subdirs containing files to process. Each subdir is examined for DICOM files (in the simplest sense by a file extension mapping) and either the head, tail, middle (or other indexed) file is examined for its tag information.

Optionally, the tag list can be constrained either by passing a ``<tagFile>`` containing a line-by-line list of tags to query, or by passing a comma separated list of tags directly.

Finally, an image conversion can also be performed (and embedded within the output html file, if an html conversion is specified).

Installation
------------

Dependencies
~~~~~~~~~~~~

The following dependencies are installed on your host system/python3 virtual env (they will also be automatically installed if pulled from pypi):

-  ``pfmisc`` (various misc modules and classes for the pf* family of objects)
-  ``pftree`` (create a dictionary representation of a filesystem hierarchy)
-  ``pfdicom`` (handle underlying DICOM file reading)
-  ``matplotlib`` (handle saving / conversion to image formats for html reports)

Using ``PyPI``
~~~~~~~~~~~~~~

The best method of installing this script and all of its dependencies is
by fetching it from PyPI

.. code:: bash

        pip3 install pfdicom_tagExtract

Command line arguments
----------------------

.. code:: html

        --inputDir <inputDir>
        Input directory to examine. The downstream nested structure of this
        directory is examined and recreated in the <outputDir>.

        [--outputDir <outputDir>]
        The directory to contain a tree structure identical to the input
        tree structure, and which contains all output files from the
        per-input-dir processing.

        [--outputFileStem <stem>]
        An output file stem pattern to use


        [--maxdepth <dirDepth>]
        The maximum depth to descend relative to the <inputDir>. Note, that
        this counts from zero! Default of '-1' implies transverse the entire
        directory tree.

        [--relativeDir]
        A flag argument. If passed (i.e. True), then the dictionary key values
        are taken to be relative to the <inputDir>, i.e. the key values
        will not contain the <inputDir>; otherwise the key values will
        contain the <inputDir>.

        [--inputFile <inputFile>]
        An optional <inputFile> specified relative to the <inputDir>. If
        specified, then do not perform a directory walk, but target this
        specific file.

        [--fileFilter <someFilter1,someFilter2,...>]
        An optional comma-delimated string to filter out files of interest
        from the <inputDir> tree. Each token in the expression is applied in
        turn over the space of files in a directory location according to a
        logical operation, and only files that contain this token string in
        their filename are preserved.

        [--filteFilterLogic AND|OR]
        The logical operator to apply across the fileFilter operation. Default
        is OR.

        [--dirFilter <someFilter1,someFilter2,...>]
        An additional filter that will further limit any files to process to
        only those files that exist in leaf directory nodes that have some
        substring of each of the comma separated <someFilter> in their
        directory name.

        [--dirFilterLogic AND|OR]
        The logical operator to apply across the dirFilter operation. Default
        is OR.

        [--outputLeafDir <outputLeafDirFormat>]
        If specified, will apply the <outputLeafDirFormat> to the output
        directories containing data. This is useful to blanket describe
        final output directories with some descriptive text, such as
        'anon' or 'preview'.

        This is a formatting spec, so

            --outputLeafDir 'preview-%%s'

        where %%s is the original leaf directory node, will prefix each
        final directory containing output with the text 'preview-' which
        can be useful in describing some features of the output set.

        [--threads <numThreads>]
        If specified, break the innermost analysis loop into <numThreads>
        threads. Please note the following caveats:

            * Only thread if you have a high CPU analysis loop. Note that
              the input file read and output file write loops are not
              threaded -- only the analysis loop is threaded. Thus, if the
              bulk of execution time is in file IO, threading will not
              really help.

            * Threading will change the nature of the innermost looping
              across the problem domain, with the result that *all* of the
              problem data will be read into memory! That means potentially
              all the target input file data across the entire input directory
              tree.

        [--json]
        If specified, do a JSON dump of the entire return payload.

        [--followLinks]
        If specified, follow symbolic links.

        [--overwrite]
        If specified, allow for overwriting of existing files

        [--man]
        Show full help.

        [--synopsis]
        Show brief help.

        [--verbosity <level>]
        Set the app verbosity level. This ranges from 0...<N> where internal
        log messages with a level=<M> will only display if M <= N. In this
        manner increasing the level here can be used to show more and more
        debugging info, assuming that debug messages in the code have been
        tagged with a level.

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

Examples
--------

    Extract DICOM header info down an input tree and save reports
    to output tree:

        pfdicom_tagExtract                                                      \
                --inputDir /var/www/html/normsmall                              \
                --fileFilter dcm                                                \
                --outputDir /var/www/html/tag                                   \
                --outputFileStem '%_md5|6_PatientID-%PatientAge'                \
                --imageFile 'm:%_md5|6_PatientID-%PatientAge.jpg'               \
                --outputFileType raw,json,html,dict,col,csv                     \
                --imageScale 3:none                                             \
                --useIndexhtml                                                  \
                --outputFileType raw,json,html,dict,col,csv                     \
                --threads 0 --verbosity 1

    will process only the "middle" DICOM file (dcm) in each series directory
    down the tree /var/www/html/normsmall, producing a jpg image of the DICOM
    as well as a series of output report formats with progressive results
    shown in the terminal. Use a --json flag to get only JSON results.

    The script can also be instructed to not process files into outputs, but to
    only print the DICOM tag information to screen of a given DICOM file
    <DCMfile>:

        pfdicom_tagExtract                                                      \
            --verbosity 0 --inputDir ./  --printToScreen                        \
            --inputFile <DCMfile>

