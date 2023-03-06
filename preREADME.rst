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

INSERT_USAGE_HERE

Changelog
---------
0.0.1 (2023-03-06)

* Initial release





