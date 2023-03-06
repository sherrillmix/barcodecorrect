.PHONY: install test

README.rst: barcodecorrect//*.py preREADME.rst setup.py makeReadme.py
	cp preREADME.rst README.rst
	make install
	python makeReadme.py
	make install

test:
	python setup.py test
install:
	python setup.py install --user
