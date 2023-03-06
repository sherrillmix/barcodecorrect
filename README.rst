barcodecount
==========

Some python functions to correct 10x barcoded samples and split reads into individual sample files.
 
Installation
------------

Github
~~~~~~

To install the development version from github, clone the repository to a local directory using something like::

    git clone https://github.com/sherrillmix/barcodecorrect.git

and run `setup.py` from the resulting directory (the `--user` installs it locally and doesn't require root access)::

  cd dnapy
  python setup.py install --user
  python setup.py test

To use the scripts directly from command line, e.g. `countbarcodes file.fastq`, (and to pass all tests above), you will need to make sure that your PATH contains the bin directory installed in by `setup.py` above. On Linux, this would mean putting something like::

   if [ -d "$HOME/.local/bin" ] ; then
       PATH="$HOME/.local/bin:$PATH"
   fi

in your `.bashrc` or `.profile`.

Usage
-----
The package provides the scripts:

barcodecorrect
~~~~

::
  
  usage: barcodecorrect [-h] -b BARCODECOUNTS [-s START] [-e END]
                        [-t BARCODE_CONFIDENCE_THRESHOLD] [-d DOTS]
                        fastqFile
  
  A function to read in a fastq file and use 10x algorithm to correct barcodes
  based on abundance of barcodes differing by a single base and quality scores
  
  positional arguments:
    fastqFile             a fastq file (potentially gzipped) containing the
                          sequence reads containing barcodes to be checked
  
  optional arguments:
    -h, --help            show this help message and exit
    -b BARCODECOUNTS, --barcodeCounts BARCODECOUNTS
                          a headerless csv file giving barcode,count in each row
    -s START, --start START
                          Start position of barcode in reads (1-based)
    -e END, --end END     End position of barcode in reads (1-based)
    -t BARCODE_CONFIDENCE_THRESHOLD, --barcode_confidence_threshold BARCODE_CONFIDENCE_THRESHOLD
                          Replace the observed barcode with the whitelist
                          barcode with the highest posterior probability that
                          exceeds this value
    -d DOTS, --dots DOTS  output dot to stderr every X reads. Input a negative
                          number to suppress output (default:-1)
  
splitreads
~~~~

::
  
  usage: splitreads [-h] -c BARCODECORRECTIONS -b BARCODEASSIGNMENTS
                    [-o OUTPUTPATH] -s SUFFIXES [-d DOTS] [-a]
                    fastqFiles [fastqFiles ...]
  
  A function to read in correct barcodes, barcode to sample assignments and
  split fastq file(s) into appropriate files
  
  positional arguments:
    fastqFiles            a fastq file(s) (potentially gzipped) containing the
                          sequence reads to be split. All fastq files must have
                          the reads in the same order
  
  optional arguments:
    -h, --help            show this help message and exit
    -c BARCODECORRECTIONS, --barcodeCorrections BARCODECORRECTIONS
                          a headerless csv file giving read name,original
                          barcode,corrected barcode in each row i.e. the output
                          of barcodecorrect
    -b BARCODEASSIGNMENTS, --barcodeAssignments BARCODEASSIGNMENTS
                          a headerless csv file giving barcode,sample assignment
                          in each row
    -o OUTPUTPATH, --outputPath OUTPUTPATH
                          a string giving the desired output directory
    -s SUFFIXES, --suffixes SUFFIXES
                          a comma separated list of suffixes the same length as
                          the fastqFiles to use for a suffix in creating output
                          files e.g. R1,R2
    -d DOTS, --dots DOTS  output dot to stderr every X reads. Input a negative
                          number to suppress output (default:-1)
    -a, --append          if set then append to already existing output files
  

Changelog
---------
0.0.1 (2023-03-06)

* Initial release





