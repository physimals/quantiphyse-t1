"""
Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

import sys
import os
import time
import traceback
import re
import tempfile
import math

import numpy as np
from PySide import QtCore, QtGui

from quantiphyse.gui.widgets import QpWidget, HelpButton, BatchButton, OverlayCombo, ChoiceOption, NumericOption, NumberList, LoadNumbers, OrderList, OrderListButtons, Citation, TitleWidget, RunBox
from quantiphyse.gui.dialogs import TextViewerDialog, error_dialog, GridEditDialog
from quantiphyse.analysis import Process
from quantiphyse.utils import debug, warn, get_plugins
from quantiphyse.utils.exceptions import QpException
from quantiphyse.utils.batch import parse_batch

from ._version import __version__

def get_model_lib(name="t1"):
    plugindir = os.path.abspath(os.path.dirname(__file__))
    if sys.platform.startswith("win"):
        template = "%s.dll"
    elif sys.platform.startswith("darwin"):
        template = "lib%s.dylib"
    else:
        template = "lib%s.so"
    return os.path.join(plugindir, template % "fabber_models_%s" % name)

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class FabberT1Widget(QpWidget):
    """
    T1 from VFA images, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="T1", icon="fabber",  group="Fabber", desc="T1 mapping from VFA images", **kwargs)
        
    def init_ui(self):
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        try:
            self.FabberProcess = get_plugins("processes", "FabberProcess")[0]
        except:
            self.FabberProcess = None

        if self.FabberProcess is None:
            vbox.addWidget(QtGui.QLabel("Fabber core library not found.\n\n You must install Fabber to use this widget"))
            return
        
        title = TitleWidget(self, help="fabber-t1", subtitle="T1 mapping from VFA images using the Fabber process %s" % __version__)
        vbox.addWidget(title)
              
        cite = Citation(FAB_CITE_TITLE, FAB_CITE_AUTHOR, FAB_CITE_JOURNAL)
        vbox.addWidget(cite)

        grid = QtGui.QGridLayout()
        self.tr = NumericOption("TR", grid, ypos=0, initial=, minval=0, step=0.1, decimals=2)
        grid.addWidget(QtGui.QLabel("FAs (\N{DEGREE SIGN})"), 1, 0)
        self.fas = NumberList(initial=[120,])
        grid.addWidget(self.fas, 1, 1)
        grid.setColumnStretch(3, 1)

        vbox.addLayout(grid)

        self.run = RunBox(self.get_process, self.get_rundata)
        vbox.addWidget(self.run)

    def get_process(self):
        return self.FabberProcess(self.ivm)

    def get_rundata(self):
        # General defaults
        rundata = {}
        rundata["loadmodels"] = get_model_lib()
        rundata["save-mean"] = ""
        rundata["save-model-fit"] = ""
        rundata["noise"] = "white"
        rundata["max-iterations"] = "20"
        rundata["model"] = "vfa"
        
        return self.rundata
