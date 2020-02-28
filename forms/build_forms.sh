#!/bin/sh
for file in *.ui ; do pyuic5 $file --import-from . -o `echo $file | sed 's/.ui/_ui.py/'`; done
for file in *.qrc ; do pyrcc5 $file -o `echo $file | sed 's/.qrc/_rc.py/'`; done
