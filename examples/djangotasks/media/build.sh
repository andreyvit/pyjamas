#!/bin/sh
# you will need to read the top level README, and run boostrap.py
# and buildout in order to make pyjsbuild

options="$*"
if [ -z $options ] ; then options="-O";fi
../../../bin/pyjsbuild $options TodoApp
