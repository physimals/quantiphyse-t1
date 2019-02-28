"""
CEST Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""
import os

from .widgets import FabberT1Widget, T10Widget
from .process import T10Process
from .tests import T10WidgetTest

QP_MANIFEST = {
    "widgets" : [T10Widget, FabberT1Widget],
    "widget-tests" : [T10WidgetTest,],
    "processes" : [T10Process],
    "fabber_dirs" : [os.path.dirname(__file__)],
}
