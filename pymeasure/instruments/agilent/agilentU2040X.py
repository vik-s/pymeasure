#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import (Instrument,
                                   RangeException)
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_discrete_set,
                                              strict_range)
import numpy as np


class AgilentU2040X(Instrument):
    """ Represents a programmatic interface to the Agilent/Keysight U2040X Series Wideband Dynamic Range Power Sensors.

    .. code-block:: python

        from pymeasure.instruments.agilent import AgilentU2040X

        put code block here
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Keysight U2040X Series wideband dynamic range power sensor.",
            **kwargs
        )
        self.freq_unit = 'GHz'

    @property
    def freq(self):
        """
        Control the frequency setting of power meter. The supported frequency range depends on the instrument option.

        .. code-block:: python

            pm.freq_unit = 'MHz' # (default = GHz)
            pm.freq = 915
        """
        value = self.ask('FREQ?')
        return value

    @freq.setter
    def freq(self, value):
        self.write('FREQ {}{}'.format(value, self.freq_unit))

    continuous_mode = Instrument.control(
        'INIT:CONT?', 'INIT:CONT %s',
        """
        Control continuous triggering of the power sensor.

        :code:`OFF`- the trigger system remains in the idle state until it is set to ON, or :meth:`~.AgilentU2040X.init` is received. Once this trigger cycle is complete, the trigger system returns to the idle state.

        :code:`ON`- the trigger system is initiated and exits the idle state. On completion of each trigger cycle, the trigger system immediately commences another trigger cycle without entering the idle state.

        .. code-block:: python

            pm.continuous_mode = 'OFF'
        """,
        validator=strict_discrete_set,
        values=['OFF', 'ON']
    )

    def init(self):
        """
        Triggers the power measurement.

            .. code-block:: python

                pm.init()
        """
        self.write('INIT:IMM')

    read = Instrument.measurement(
        'READ?',
        """
        Read the power value after the measurement started using :meth:`~.AgilentU2040X.init` has completed.

        .. code-block:: python

            power_value = pm.read
        """
    )
