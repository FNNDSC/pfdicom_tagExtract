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

        -I|--inputDir <inputDir>
        Input DICOM directory to examine. By default, the first file in this
        directory is examined for its tag information. There is an implicit
        assumption that each <inputDir> contains a single DICOM series.

        -i|--inputFile <inputFile>
        An optional <inputFile> specified relative to the <inputDir>. If
        specified, then do not perform a directory walk, but convert only
        this file.

        -e|--extension <DICOMextension>
        An optional extension to filter the DICOM files of interest from the
        <inputDir>.

        [-O|--outputDir <outputDir>]
        The directory to contain all output files.

        [--outputLeafDir <outputLeafDirFormat>]
        If specified, will apply the <outputLeafDirFormat> to the output
        directories containing data. This is useful to blanket describe
        final output directories with some descriptive text, such as
        'anon' or 'preview'.

        This is a formatting spec, so

            --outputLeafDir 'preview-%s'

        where %s is the original leaf directory node, will prefix each
        final directory containing output with the text 'preview-' which
        can be useful in describing some features of the output set.

        -F|--tagFile <tagFile>
        Read the tags, one-per-line in <tagFile>, and print the
        corresponding tag information in the DICOM <inputFile>.

        -T|--tagList <tagList>
        Read the list of comma-separated tags in <tagList>, and print the
        corresponding tag information parsed from the DICOM <inputFile>.

        -m|--image <[<index>:]imageFile>
        If specified, also convert the <inputFile> to <imageFile>. If the
        name is preceded by an index and colon, then convert this indexed
        file in the particular <inputDir>.

        [-s|--imageScale <factor:interpolation>]
        If an image conversion is specified, this flag will scale the image
        by <factor> and use an interpolation <order>. This is useful in
        increasing the size of images for the html output.

        Note that certain interpolation choices can result in a significant
        slowdown!

            interpolation order:

            'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'

        -o|--outputFileStem <outputFileStem>
        The output file stem to store data. This should *not* have a file
        extension, or rather, any "." in the name are considered part of
        the stem and are *not* considered extensions.

        [-t|--outputFileType <outputFileType>]
        A comma specified list of output types. These can be:

            o <type>    <ext>       <desc>
            o raw       -raw.txt    the raw internal dcm structure to string
            o json      .json       a json representation
            o html      .html       an html representation with optional image
            o dict      -dict.txt   a python dictionary
            o col       -col.txt    a two-column text representation (tab sep)
            o csv       .csv        a csv representation

        Note that if not specified, a default type of 'raw' is assigned.

        [-p|--printToScreen]
        If specified, will print tags to screen.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

        [--version]
        If specified, print the version number and exit.

        [--json]
        If specified, output a JSON dump of final return.

        [--followLinks]
        If specified, follow symbolic links.

        -v|--verbosity <level>
        Set the app verbosity level.

            0: No internal output;
            1: Run start / stop output notification;
            2: As with level '1' but with simpleProgress bar in 'pftree';
            3: As with level '2' but with list of input dirs/files in 'pftree';
            5: As with level '3' but with explicit file logging for
                    - read
                    - analyze
                    - write

Examples
--------

Run on a target tree and output some detail and stats

.. code:: bash

        pfdicom_tagExtract                                      \
                    -I /var/www/html/normsmall -e dcm           \
                    -O /var/www/html/tag                        \
                    -o '%_md5|6_PatientID-%PatientAge'          \
                    -m 'm:%_nospc|-_ProtocolName.jpg'           \
                    -s 3:none                                   \
                    --useIndexhtml                              \
                    -t raw,json,html,dict,col,csv               \
                    --threads 0 -v 0 --json

which will output only at script conclusion and will log a JSON formatted string.
