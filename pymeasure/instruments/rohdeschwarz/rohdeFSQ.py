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


class RohdeFSQ(Instrument):
    """ Instrument code to control a Rohde & Schwarz FSQ Signal Analyzer

    .. code-block:: python

        from pymeasure.instruments.rohdeschwarz import RohdeFSQ

        sa = RohdeFSQ("GPIB0::20", read_termination = '\\n',
                      write_termination = '\\n', timeout=None)

        # reset instrument to clear previous settings.
        sa.reset()

        # set freq and power units
        sa.freq_unit = "MHz"
        sa.power_unit = "DBM"

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
            "Rohde & Schwarz FSQ RF Signal Analyzer",
            **kwargs
        )
        self.freq_unit = "GHz"

#################
# SENSE SUBSYSTEM
#################

    ############
    # FREQUENCY
    ############

    @property
    def center_freq(self):
        """
        Control the center frequency of the analyzer.

        Units must be set by assigning `self.freq_unit` to a frequency unit string, eg. :code:`MHz', :code:`GHz`. Allowed value of frequencies depends on the instrument frequency range.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.center_freq = 915
            sa.center_freq          # this returns a purely numeric freq value
        """
        value = self.ask(":FREQ:CENT?")
        return value

    @center_freq.setter
    def center_freq(self, value):
        self.write(":FREQ:CENT {}{}".format(value, self.freq_unit))

    @property
    def freq_span(self):
        """
        Control the frequency span of the analyzer.

        Units must be set by assigning `self.freq_unit` to a frequency unit string, eg. :code:`MHz', :code:`GHz`. Allowed value of frequencies depends on the instrument frequency range.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.freq_span = 10
            sa.freq_span          # this returns a purely numeric freq value
        """
        value = self.ask(":FREQ:SPAN?")
        return value

    @freq_span.setter
    def freq_span(self, value):
        self.write(":FREQ:SPAN {}{}".format(value, self.freq_unit))

    freq_mode = Instrument.control(
        'FREQ:MODE?', 'FREQ:MODE %s',
        """
        In analyzer mode, this command switches between frequency domain (SWEEP) and time domain (FIXED).

        -Values: :code:`FIXED`, :code:`SWEEP` (default).

        .. code-block:: python

            sa.freq_mode = 'SWEEP'
        """,
        validator=strict_discrete_set,
        values=['FIXED', 'SWEEP'],
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

    @property
    def freq_start(self):
        """
        This command defines the start frequency of the R&S FSQ. This command is only available in the frequency domain.

        Units must be set by assigning `self.freq_unit` to a frequency unit string, eg. :code:`MHz', :code:`GHz`. Allowed value of frequencies depends on the instrument frequency range.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.freq_start = 500
            sa.freq_start          # this returns a purely numeric freq value
        """
        value = self.ask(":FREQ:STAR?")
        return value

    @freq_start.setter
    def freq_start(self, value):
        self.write(":FREQ:STAR {}{}".format(value, self.freq_unit))

    @property
    def freq_stop(self):
        """
        This command defines the stop frequency of the R&S FSQ. This command is only available in the frequency domain.

        Units must be set by assigning `self.freq_unit` to a frequency unit string, eg. :code:`MHz', :code:`GHz`. Allowed value of frequencies depends on the instrument frequency range.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.freq_stop = 1500
            sa.freq_stop          # this returns a purely numeric freq value
        """
        value = self.ask(":FREQ:STOP?")
        return value

    @freq_stop.setter
    def freq_stop(self, value):
        self.write(":FREQ:STOP {}{}".format(value, self.freq_unit))

    #########
    # AVERAGE
    #########

    average_count = Instrument.control(
        'AVER:COUN?', 'AVER:COUN %s',
        """
        This command defines the number of measurements which contribute to the average value. It should be noted that continuous averaging will be performed after the indicated number has been reached in continuous-sweep mode.

        In single-sweep mode, the sweep is stopped as soon as the indicated number of measurements (sweeps) is reached. Synchronization to the end of the indicated number of measurements is only possible in single-sweep mode.

        .. code-block:: python

            sa.average_count = 10       # take 10 averages
            sa.average_count            # returns numeric value
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 32767, 1),
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

    averaging = Instrument.control(
        'AVER?', 'AVER: %s',
        """
        This command switches on or off the average calculation. :code:`OFF`/:code:`ON` is used to turn off/on averaging. While querying the status of averaging, a 0 (off) or 1 (on) is returned.

        -Values: :code:`OFF`(default), :code:`ON`

        .. code-block:: python

            sa.averaging = 'ON'     # turns on 10 averages
            sa.averaging            # returns 1 if averaging is on, 0 otherwise
        """,
        validator=strict_discrete_set,
        values=['OFF', 'ON'],
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

    average_type = Instrument.control(
        'AVER:TYPE?', 'AVER:TYPE %s',
        """
        This command selects the type of average function. If :code:`VIDEO` is selected, the logarithmic power is averaged and, if :code:`LINEAR` is selected, the power values are averaged before they are converted to logarithmic values.

        -Values: :code:`VIDEO`(default), :code:`LINEAR`

        .. code-block:: python

            sa.average_type = 'VIDEO'
        """,
        validator=strict_discrete_set,
        values=['VIDEO', 'LINEAR'],
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

    #######
    # SWEEP
    #######

    sweep_count = Instrument.control(
        'SWE:COUN:CURR?', 'SWE:COUN %s',
        """
        This command defines the number of sweeps started with single sweep, which are used for calculating the average or maximum value. In average mode, the value 0 defines a continuous averaging of measurement data over 10 sweeps.

        .. code-block:: python

            sa.sweep_count = 10       # take 10 sweeps to find avg or max value
            sa.sweep_count            # returns numeric value
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 32767, 1),
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

    sweep_points = Instrument.control(
        'SWE:POIN?', 'SWE   :POIN %s',
        """
        This command defines the number of measurement points for one sweep run.

        -Values: :code:`155`, :code:`313`, :code:`625` (default), :code:`1251`, :code:`1999`, :code:`2501`, :code:`5001`, :code:`10001`, :code:`20001`, :code:`30001`

        .. code-block:: python

            sa.sweep_points = 10       # take 10 sweeps to find avg or max value
            sa.sweep_points            # returns numeric value
        """,
        validator=strict_discrete_set,
        values=[155, 313, 625, 1251, 1999, 2501, 5001, 10001, 20001, 30001],
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

    ###########
    # BANDWIDTH
    ###########

    @property
    def res_bw(self):
        """
        This command defines the resolution bandwidth of the R&S FSQ. 

        Units must be set by assigning `self.freq_unit` to a frequency unit string, eg. :code:`MHz', :code:`GHz`. Allowed value of frequencies depends on the instrument frequency range.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.res_bw = 1

        """
        value = self.ask("BAND?")
        return value

    @res_bw.setter
    def res_bw(self, value):
        self.write("BAND {}{}".format(value, self.freq_unit))

    @property
    def video_bw(self):
        """
        This command defines the video bandwidth of the R&S FSQ. 

        Units must be set by assigning `self.freq_unit` to a frequency unit string, eg. :code:`MHz', :code:`GHz`. Allowed value of frequencies depends on the instrument frequency range.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.video_bw = 1

        """
        value = self.ask("BAND:VID?")
        return value

    @video_bw.setter
    def video_bw(self, value):
        self.write("BAND:VID {}{}".format(value, self.freq_unit))

##################
# SYSTEM SUBSYSTEM
##################

    display_update = Instrument.setting(
        'SYST:DISP:UPD %s',
        """
        Turn on/off display updates on the instrument screen during remote operation. Default = :code:`OFF`.

        - Values: :code:`OFF`, :code:`ON`

        .. code-block:: python

            sa.display_update = 'ON'
        """,
        validator=strict_discrete_set,
        values=['OFF', 'ON'],
        map_values=False,
        check_get_errors=True,
        check_set_errors=True
    )

##########
# INITIATE
##########

    continuous_mode = Instrument.control(
        'INIT:CONT?', 'INIT:CONT %s',
        """
        This command determines whether the trigger system is continuously initiated (continuous) or performs single measurements (single).

        -Values: :code:`OFF`, :code:`ON` (default)

        .. code-block:: python

            sa.continuous_mode = 'OFF'
        """,
        validator=strict_discrete_set,
        values=['OFF', 'ON'],
        map_values=False,
        check_set_errors=True,
        check_get_errors=True
    )

    def init(self):
        """
        The command initiates a new sweep.

        With Sweep Count > 0 or Average Count > 0, this means a restart of the indicated number of measurements. With trace functions MAXHold, MINHold and AVERage, the previous results are reset on restarting the measurement.

        In single-sweep mode, synchronization to the end of the indicated number of measurements can be achieved with the command *OPC, *OPC? or *WAI. In continuous-sweep mode, synchronization to the sweep end is not possible since the overall measurement never ends. This method automatically handles this.

        .. code-block:: python

            sa.init()
        """
        if (int(self.continuous_mode) == 1):
            self.write('INIT')
        else:
            self.write('INIT;*OPC?')

###########
# CALCULATE
###########

    def peak_search(self, num):
        """
        This finds the peak of a particular marker.

        .. code-block:: python

            sa.peak_search(1)
        """
        num_value = _validate_marker_number(num)
        self.write('CALC:MARK{}:PEAK'.format(num_value))

    ###########
    # HARMONICS
    ###########

    measure_harmonics = Instrument.setting(
        'CALC:MARK:FUNC:HARM %s',
        """
        This command switches on or off the measurement of the harmonics of a carrier signal. The carrier signal is the first harmonic. The function is independent of the marker selection.

        -Values: :code:`OFF` (default), :code:`ON`

        .. code-block:: python

            sa.measure_harmonics = 'ON'
        """,
        validator=strict_discrete_set,
        values=['OFF', 'ON']
    )

    nharmonics = Instrument.setting(
        'CALC:MARK:FUNC:HARM:NHARM %s',
        """
        This command defines the number of harmonics of a carrier signal to be measured.

        .. code-block:: python

            sa.nharmonics = 3
        """,
        validator=truncated_discrete_set,
        values=np.arange(1, 26, 1),
    )

    def get_harmonics(self, harmonic_power='Relative'):
        """
        This command reads out the list of harmonics. This is only possible in the single-sweep mode.

        :param harmonic_power: Set the harmonic level output to be :code:`Relative` in dB to the fundamental carrier power in dBm, or convert the harmonic power into :code:`Absolute` power values with units dBm.

        :returns value: Fundamental and harmonic tone power values.

        :rtype: List

        .. code-block:: python

            sa.get_harmonics(harmonic_power='Absolute')
        """
        validator = strict_discrete_set
        values = ['Relative', 'Absolute']
        hpwr = validator(harmonic_power, values)
        read_value = self.ask('CALC:MARK:FUNC:HARM:LIST?')

        # create a list of harmonic values
        listharm = [float(x) for x in read_value.split(',')]

        # filter out the invalid -200 values that are returned
        harm = [x for x in listharm if x != -200]

        if hpwr == 'Relative':
            return harm
        else:
            # convert to absolute power in dBm
            abs_harm = [harm[0]+x for x in harm[1:]]
            # add back the fundamental tone power
            abs_harm.insert(0, harm[0])
            return abs_harm

    #########
    # MARKERS
    #########

    def marker_state(self, num, state):
        """
        This command switches on or off the selected marker.

        :param num: Up to 4 markers allowed (1, 2, 3, 4).
        :param state: :code:`ON`, :code:`OFF`

        .. code-block:: python

            sa.marker_state(num=2, state='ON')
        """

        num_value = _validate_marker_number(num)

        state_validator = strict_discrete_set
        state_values = ['OFF', 'ON']
        state_value = state_validator(state, state_values)

        self.write("CALC:MARK{} {}".format(num_value, state_value))

    def put_marker_at_freq(self, num, freq):
        """
        This command positions the selected marker to the indicated frequency.

        :param num: Marker to be assigned at particular frequency
        :param freq: Frequency with units defined by :code:`self.freq_unit`.

        .. code-block:: python

            sa.freq_unit = 'MHz'
            sa.put_marker_at_freq(num=2, freq=900)
        """
        num_value = _validate_marker_number(num)

        self.write("CALC:MARK{}:X {}{}".format(
            num_value, freq, self.freq_unit))

    def get_y_at_marker(self, num):
        """
        This command queries the measured value of the selected marker in the indicated measurement window. This is only possible in single-sweep mode.

        :param num: Marker whose y value needs to be obtained.

        :returns value: Power output in the unit determined with the CALCulate<1|2>:UNIT:POWer command.

        :rtype: float

        .. code-block:: python

            output_power = sa.get_y_at_marker(2)
        """

        num_value = _validate_marker_number(num)

        value = self.ask("CALC:MARK{}:Y?".format(num_value))
        return float(value)

    def all_markers_off(self):
        """
        This command switches off all active markers in the indicated measurement window.

        .. code-block:: python

            sa.all_markers_off()
        """
        self.write('CALC:MARK:AOFF')

    freq_counter = Instrument.setting(
        'CALC:MARK1:COUN %s',
        """
        This command switches on or off the frequency counter at the marker position in the selected measurement window. 
        
        Frequency counting is possible only for marker 1 in every measurement window. It should be noted that a complete sweep must be performed after switching on the frequency counter to ensure that the frequency to be measured is actually reached. The synchronization to the sweep end required for this is possible only in single-sweep mode.

        .. code-block:: python

            sa.freq_counter = 'ON'      # turn on counting for marker 1 only
        """,
        validator=strict_discrete_set,
        values=['OFF', 'ON']
    )

    get_freq_at_marker = Instrument.measurement(
        'CALC:MARK:COUN:FREQ?',
        """
        This command queries the result of the frequency counter for marker 1 in the selected measurement window. 
        
        Before the command, the frequency counter should be switched on using :meth:`~.RohdeFSQ.freq_counter`and a complete measurement performed using :meth:`~.RohdeFSQ.init` to obtain a valid count result. Therefore, a single sweep with synchronization must be performed between switching on the frequency counter and querying the count result. 

        .. code-block:: python

            marker_freq = sa.get_freq_at_marker
        """
    )

    def set_ref_at_marker_level(self, num):
        """
        This command sets the reference level to the power measured by the indicated marker.

        .. code-block:: python

            sa.set_ref_at_marker_level()
        """
        num_value = _validate_marker_number(num)
        self.write('CALC:MARK{}:FUNC:REF'.format(num_value))

    def set_center_freq_at_marker_freq(self, num):
        """
        This command sets the center frequency of the selected measurement window equal to the frequency of the indicated marker.

        .. code-block:: python

            sa.set_center_freq_at_marker_freq(1)
        """
        num_value = _validate_marker_number(num)
        self.write('CALC:MARK{}:FUNC:CENT'.format(num_value))

#######
# UNIT
#######

    power_unit = Instrument.setting(
        'UNIT:POW %s',
        """
        This command selects the unit for power for the measurement window.

        -Values: :code:`DBM` | :code:`DBPW` | :code:`WATT` | :code:`DBUV` | :code:`DBMV` | :code:`VOLT` | :code:`DBUA` | :code:`AMP` | :code:`V` | :code:`A` | :code:`W` | :code:`DB` | :code:`DBPT` | :code:`PCT` | :code:`UNITLESS` | :code:`DBUV_MHZ` | :code:`DBMV_MHZ` | :code:`DBUA_MHZ` | :code:`DBUV_M` | :code:`DBUA_M` | :code:`DBUV_MMHZ` | :code:`DBUA_MMHZ`

        .. code-block:: python

            sa.power_unit = 'DBM'
        """,
        validator=strict_discrete_set,
        values=['DBM', 'DBPW', 'WATT', 'DBUV', 'DBMV', 'VOLT', 'DBUA', 'AMP', 'V', 'A', 'W', 'DB', 'DBPT',
                'PCT', 'UNITLESS', 'DBUV_MHZ', 'DBMV_MHZ', 'DBUA_MHZ', 'DBUV_M', 'DBUA_M', 'DBUV_MMHZ', 'DBUA_MMHZ']
    )

#########
# DISPLAY
#########

    ref_offset_db = Instrument.control(
        'DISP:TRAC:Y:RLEV:OFFS', 'DISP:TRAC:Y:RLEV:OFFS %sdB',
        """
       This command defines the offset of the reference level in the selected measurement window in dB.

       .. code-block:: python

        sa.ref_offset = 10
       """,
        validator=strict_range,
        values=[-200, 200]
    )


def _validate_marker_number(num):
    num_validator = strict_range
    num_values = np.arange(1, 4, 1)
    num_value = num_validator(num, num_values)
    return num_value
