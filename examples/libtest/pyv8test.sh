#!/bin/sh
python ../../pyv8/pyv8run.py  --dynamic '^I18N[.].*.._..' $@ LibTest `find I18N -name ??_??.py` -d

