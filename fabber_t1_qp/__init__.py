"""
CEST Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from .widget import FabberT1Widget, get_model_lib

QP_MANIFEST = {
    "widgets" : [FabberT1Widget],
    "fabber-libs" : [get_model_lib("t1")]
}
