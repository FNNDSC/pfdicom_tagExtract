pfdicom_tagExtract
==================

Quick Overview
--------------

-  pfdicom_tagExtract generates reports in various formats based on DICOM tags

Overview
--------

pfdicom_tagExtract extracts the header information of DICOM files and echoes to stdout as well as to an output report-type file -- this can be a raw output, a json-type output, or html-type output.

The script accepts an <inputDir>, and then from this point an os.walk  is performed to extract all the subdirs. Each subdir is examined for DICOM files (in the simplest sense by a file extension mapping) and either the head, tail, middle (or other indexed) file is examined for its tag information.

Optionally, the tag list can be constrained either by passing a <tagFile> containing a line-by-line list of tags to query, or by passing a comma separated list of tags directly.

Finally, an image conversion can also be performed (and embedded within the output html file, if an html conversion is specified).

Dependencies
------------

The following dependencies are installed on your host system/python3 virtual env (they will also be automatically installed if pulled from pypi):

-  pfmisc (various misc modules and classes for the pf* family of objects)
-  pftree (create a dictionary representation of a filesystem hierarchy)
-  pfidcom (handle underlying DICOM file reading)
-  matplotlib (handle saving / conversion to image formats for html reports)

Installation
~~~~~~~~~~~~

The best method of installing this script and all of its dependencies is
by fetching it from PyPI

.. code:: bash

        pip3 install pfdciom_tagExtract

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

        NOTE: If neither -F nor -T are specified, a '-r raw' is
        assumed.

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

        [-p|--printToScreen]
        If specified, will print tags to screen.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

        -v|--verbosity <level>
        Set the app verbosity level. 

             -1: No internal output.
              0: All internal output.


Examples
~~~~~~~~

Run on a target tree and output some detail and stats

.. code:: bash

        pfdicom         -I /var/www/html/normative              \
                        -e dcm                                  \
                        -O /var/www/html/tag2                   \
                        -t raw,json,html,dict,col,csv           \
                        -o %PatientAge-%_md5.6_PatientID        \ 
                        -m m:%PatientAge-%_md5.6_PatientID.jpg 
 
