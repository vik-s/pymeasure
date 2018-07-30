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

######
# MAIN
######


class RohdeSMB100A(Instrument):
    """ Instrument code to control a Rohde & Schwarz SMB100A RF Signal Generator.

    .. code-block:: python

        from pymeasure.instruments.rohdeschwarz import RohdeSMB100A

        sig = RohdeSMB100A("GPIB0::29", read_termination = '\\n', write_termination = '\\n', timeout=None)

        # reset instrument to clear previous settings.
        sig.reset()

        # set freq and power units
        sig.freq_unit = "MHz"
        sig.power_unit = "DBM"

        # set frequency and power levels
        sig.power_level = -20 #dBm
        sig.fixed_freq = 700 #MHz

        # turn on signal
        sig.output = "ON"

        # perform any measurements needed.

        # turn off signal
        sig.output = "OFF"

    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Rohde & Schwarz SMB100A RF Signal Generator",
            **kwargs
        )
        self.freq_unit = "GHz"

#######
# POWER
#######

    # RF power level
    power_level = Instrument.control(
        ":POW?", ":POW %s",
        """ Sets the RF power level in dBm applied to DUT.

        If a level offset is included, the output power level is adjusted accordingly. The power level is not checked to see if the instrument can support it because it depends on the option installed. When setting power level, please refer the operation manual to ensure that your instrument can support it at your operating frequency. Use :meth:`~.RohdeSMB100A.get_instrument_options` method to identify the options installed in the instrument.

        .. code-block:: python

            sig.power_level = -5
        """,

        check_set_errors=True,
        check_get_errors=True
    )

    # RF power offset
    power_offset = Instrument.control(
        ":POW:OFFS?", ":POW:OFFS %s",
        """ Sets the RF offset power level in dB.

        Specifies the constant level offset of a downstream attenuator/amplifier. If level offset is entered, the level entered with :meth:`~.RohdeSMB100A.power_level` no longer corresponds to the RF output level at connector.

        .. code-block:: python

            sig.power_offset = 5
        """,
        validator=truncated_discrete_set,
        values=np.arange(-100, 100, 0.01),
        check_set_errors=True,
        check_get_errors=True
    )

###########
# FREQUENCY
###########

    # fixed frequency

    @property
    def fixed_freq(self):
        """
        Sets the fixed frequency of the RF signal.

        The range of allowed frequencies depends on the instrument option, which can be checked using :meth:`~.RohdeSMB100A.get_instrument_options`.

        .. code-block:: python

            sig.fixed_freq = 1 #GHz (default)

        To change default frequency units, change the object variable `freq_unit`. For example, to set frequency to 1 MHz,

        .. code-block:: python

            sig.freq_unit = "MHz"
            sig.fixed_freq = 1
        """
        value = self.ask(":FREQ?")
        return value

    @fixed_freq.setter
    def fixed_freq(self, value):
        self.write(":FREQ {}{}".format(
            value, self.freq_unit))

########
# OUTPUT
########
    output = Instrument.setting(
        ":OUTP %s",
        """ Turns the RF output on and off.

        - Values: :code:`ON`, :code:`OFF`

        .. code-block:: python

            sig.output = "ON"
        """,
        validator=strict_discrete_set,
        values={'OFF', 'ON'},
        map_values=False,
        check_set_errors=True,
        check_get_errors=True
    )


#######
# UNITS
#######

    power_unit = Instrument.control(
        "UNIT:POW?", "UNIT:POW %s",
        """
        Defines the default unit for power parameters. This setting affects the GUI, as well as all remote control commands that determine power values.

        - Values: :code:`V`, :code:`DBUV`, :code:`DBM`

        .. code-block:: python

            sig.power_unit = "DBM" # default setting
        """,
        validator=strict_discrete_set,
        values={'V', 'DBUV', 'DBM'},
        map_values=False,
        check_set_errors=True,
        check_get_errors=True
    )

#########
# GENERAL
#########

    get_instrument_options = Instrument.measurement(
        "*OPT?",
        """ Get the options installed on instrument. 
        
        .. code-block:: python

            sig.get_instrument_options
        """
    )
