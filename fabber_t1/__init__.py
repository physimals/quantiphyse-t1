"""
CEST Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""
from quantiphyse.utils import get_local_shlib

from .widget import FabberT1Widget

QP_MANIFEST = {
    "widgets" : [FabberT1Widget],
    "fabber-libs" : [get_local_shlib("fabber_models_t1", __file__)]
}
