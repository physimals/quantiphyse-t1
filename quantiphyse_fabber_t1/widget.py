"""
Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

import sys
import os
import re

from PySide import QtCore, QtGui

from quantiphyse.gui.widgets import QpWidget, HelpButton, BatchButton, OverlayCombo, ChoiceOption, NumericOption, NumberList, LoadNumbers, OrderList, OrderListButtons, Citation, TitleWidget, RunBox
from quantiphyse.utils import get_plugins
from quantiphyse.utils.exceptions import QpException

from ._version import __version__

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class ChooseDataDialog(QtGui.QDialog):

    def __init__(self, parent, ivm, used=[]):
        super(ChooseDataDialog, self).__init__(parent)
        self.setWindowTitle("Add VFA data set")
        vbox = QtGui.QVBoxLayout()

        grid = QtGui.QGridLayout()
        grid.addWidget(QtGui.QLabel("Data set"), 0, 0)
        self.data_combo = OverlayCombo(ivm, static_only=True)

        # Default to first data which hasn't been used
        data = [i for i in range(self.data_combo.count()) if self.data_combo.itemText(i) not in used]
        if len(data) > 0: self.data_combo.setCurrentIndex(data[0]) 

        self.data_combo.currentIndexChanged.connect(self._guess_fa)
        grid.addWidget(self.data_combo, 0, 1)
        
        grid.addWidget(QtGui.QLabel("Flip angle (\N{DEGREE SIGN})"), 1, 0)
        self.fa_edit = QtGui.QLineEdit()
        self.fa_edit.textChanged.connect(self._validate)
        grid.addWidget(self.fa_edit, 1, 1)

        vbox.addLayout(grid)
        
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        vbox.addWidget(self.buttonBox)

        self.setLayout(vbox)
        self._guess_fa()
        self._validate()

    def _guess_fa(self):
        name = self.data_combo.currentText()
        m = re.search(r".*?(\d+).*$", name)
        if m is not None:
            guess = m.group(1)
        else:
            guess = ""
        self.fa_edit.setText(guess)

    def _validate(self):
        valid = True
        try:
            fa = float(self.fa_edit.text())
            self.fa_edit.setStyleSheet("")
        except:
            self.fa_edit.setStyleSheet("QLineEdit {background-color: red}")
            valid = False
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(valid)

class FabberT1Widget(QpWidget):
    """
    T1 from VFA images, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="Fabber T1", icon="fabber",  group="T1", desc="T1 mapping from VFA images using Bayesian inference", **kwargs)
        
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
        self.multivol_choice = ChoiceOption("VFA data in", grid, ypos=0, choices=["Single data set", "Multiple data sets"])
        self.multivol_choice.combo.currentIndexChanged.connect(self.update_ui)

        self.multivol_label = QtGui.QLabel("VFA data set")
        grid.addWidget(self.multivol_label, 1, 0)
        self.multivol_combo = OverlayCombo(self.ivm)
        grid.addWidget(self.multivol_combo, 1, 1)
        self.multivol_fas_label = QtGui.QLabel("FAs (\N{DEGREE SIGN})")
        grid.addWidget(self.multivol_fas_label, 2, 0)
        self.multivol_fas = NumberList(initial=[1,])
        grid.addWidget(self.multivol_fas, 2, 1, 1, 2)

        self.singlevol_label = QtGui.QLabel("VFA data sets")
        grid.addWidget(self.singlevol_label, 3, 0)
        grid.setAlignment(self.singlevol_label, QtCore.Qt.AlignTop)
        self.singlevol_table = QtGui.QTableWidget()
        self.singlevol_table.setColumnCount(2)
        self.singlevol_table.setHorizontalHeaderLabels(["Data set", "Flip angle"])
        self.singlevol_table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        grid.addWidget(self.singlevol_table, 3, 1)

        hbox = QtGui.QHBoxLayout()
        self.singlevol_add = QtGui.QPushButton("Add")
        self.singlevol_add.clicked.connect(self.add_vol)
        hbox.addWidget(self.singlevol_add)
        self.singlevol_clear = QtGui.QPushButton("Clear")
        self.singlevol_clear.clicked.connect(self.clear_vols)
        hbox.addWidget(self.singlevol_clear)
        grid.addLayout(hbox, 4, 1)
        
        self.tr = NumericOption("TR (ms)", grid, ypos=5, default=4.108, minval=0, step=0.1, decimals=3)
        
        grid.setColumnStretch(3, 1)

        vbox.addLayout(grid)

        self.run = RunBox(self.get_process, self.get_rundata)
        vbox.addWidget(self.run)

        vbox.addStretch(1)
        self.update_ui()

    def update_ui(self):
        multivol = self.multivol_choice.combo.currentIndex() == 0
        self.multivol_label.setVisible(multivol)
        self.multivol_combo.setVisible(multivol)
        self.multivol_fas_label.setVisible(multivol)
        self.multivol_fas.setVisible(multivol)

        self.singlevol_label.setVisible(not multivol)
        self.singlevol_table.setVisible(not multivol)
        self.singlevol_add.setVisible(not multivol)
        self.singlevol_clear.setVisible(not multivol)

    def add_vol(self):
        used = [self.singlevol_table.item(i, 0).text() for i in range(self.singlevol_table.rowCount())]
        dlg = ChooseDataDialog(self, self.ivm, used)
        if dlg.exec_():
            nrows = self.singlevol_table.rowCount()
            self.singlevol_table.setRowCount(nrows+1)
            self.singlevol_table.setItem(nrows, 0, QtGui.QTableWidgetItem(dlg.data_combo.currentText()))
            self.singlevol_table.setItem(nrows, 1, QtGui.QTableWidgetItem(dlg.fa_edit.text()))

    def clear_vols(self):
        self.singlevol_table.setRowCount(0)

    def get_process(self):
        return self.FabberProcess(self.ivm)

    def batch_options(self):
        return "Fabber", self.get_rundata()

    def get_rundata(self):
        rundata = {}
        rundata["model-group"] = "t1"
        rundata["save-mean"] = ""
        rundata["save-model-fit"] = ""
        rundata["noise"] = "white"
        rundata["max-iterations"] = "20"
        rundata["model"] = "vfa"
        rundata["tr"] = self.tr.spin.value()/1000

        multivol = self.multivol_choice.combo.currentIndex() == 0
        if multivol and self.multivol_combo.currentText() in self.ivm.data:
            rundata["data"] = self.multivol_combo.currentText()
            fas = self.multivol_fas.values()
            nvols = self.ivm.data[self.multivol_combo.currentText()].nvols
            if nvols != len(fas):
                raise QpException("Number of flip angles must match the number of volumes in the selected data (%i)" % nvols)
            for idx, fa in enumerate(fas):
                rundata["fa%i" % (idx+1)] = fa
        else:
            rundata["data"] = []
            for r in range(self.singlevol_table.rowCount()):
                rundata["data"].append(self.singlevol_table.item(r, 0).text())
                rundata["fa%i" % (r+1)] = float(self.singlevol_table.item(r, 1).text())

        return rundata
