# @Author: Eric Rosenthal
# @Date:   2022-02-22T16:41:43-08:00
# @Email:  ericros@stanford.edu
# @Project: nspyre-jv
# @Last modified by:   Eric Rosenthal
# @Last modified time: 2022-07-16T15:41:06-07:00



"""
Fake data acquisition system driver for demonstration purposes.

Author: Jacob Feder
Date: 12/27/2021
"""
import logging
import random

logger = logging.getLogger(__name__)

class DAQ:
    def cnts(self, key):
        """Return the number of counts received."""
        return random.randint(0, 5000)
