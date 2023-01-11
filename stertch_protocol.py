import time
# ***************************************************************************
# *                          PC-Arduino protocol                            *
# ***************************************************************************
# Pubilc
ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_REQUEST = "00"
ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE = "01"
ARDUINO_TELEGRAM_TYPE_PROGRESS_CONTROL_REQUEST = "02"
ARDUINO_TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE = "03"
ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST = "04"
ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE = "05"
ARDUINO_TELEGRAM_TYPE_ERROR_RESPONSE = "99"
ARDUINO_TELEGRAM_END = '\r\n'


# Launch test
ARDUINO_TELEGRAM_LAUNCH_TEST_REQUEST = f'{ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_REQUEST}\r\n'.encode(
    encoding='UTF-8')

# Progress control
ARDUINO_TEST_STOP = '0'
ARDUINO_TEST_START = '1'
ARDUINO_TEST_PAUSE = '2'


class ARDUINO_TELEGRAM_PROGRESS_CONTROL_REQUEST:
    def __init__(self, control_flag):
        self.control_flag = control_flag

    def __str__(self):
        return f'{ARDUINO_TELEGRAM_TYPE_PROGRESS_CONTROL_REQUEST},{self.control_flag}{ARDUINO_TELEGRAM_END}'


class ARDUINO_TELEGRAM_PROGRESS_CONTROL_RESPONSE:
    def __init__(self, control_flag):
        self.control_flag = control_flag

    def __str__(self):
        return f'{ARDUINO_TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE},{self.control_flag}{ARDUINO_TELEGRAM_END}'


# Parameter setting
class ARDUINO_TELEGRAM_PARAMETER_SETTING_REQUEST:
    def __init__(self, stretch_length, stretch_speed, cycles):
        self.stretch_length = stretch_length
        self.stretch_speed = stretch_speed
        self.cycles = cycles

    def __str__(self):
        return f'{ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST},{self.stretch_length},{self.stretch_speed},{self.cycles}{ARDUINO_TELEGRAM_END}'


# Error
ARDUINO_TELEGRAM__ERROR = f'{ARDUINO_TELEGRAM_TYPE_ERROR_RESPONSE}{ARDUINO_TELEGRAM_END}'


# ***************************************************************************
# *                          PC-PSoC protocol                               *
# ***************************************************************************
# Public
PSOC_TELEGRAM_END = '\r\n'
PSOC_TELEGRAM_TYPE_DATA_SUBSCRIPTION_REQUEST = "00"
PSOC_TELEGRAM_TYPE_DATA_SUBSCRIPTION_RESPONSE = "01"
PSOC_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST = "02"
PSOC_TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE = "03"
PSOC_TELEGRAM_TYPE_ERROR_RESPONSE = "99"

# Data subscription
PSOC_DATA_UNSUBSCRIPTION = 0
PSOC_DATA_SUBSCRIPTION = 1


class PSOC_TELEGRAM_DATA_SUBSCRIPTION_REQUEST:
    def __init__(self, subscription_status):
        ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST
        self.subscription_status = subscription_status

    def __str__(self):
        return f'{PSOC_TELEGRAM_TYPE_DATA_SUBSCRIPTION_REQUEST},{self.subscription_status}{PSOC_TELEGRAM_END}'

# Measurement setting


class PSOC_TELEGRAM_SET_PARAMETER_REQUEST:
    def __init__(self, sample_rate, downsample, gain_channel, current_source_channel):
        self.sample_rate = sample_rate
        self.downsample = downsample
        self.gain_channel = gain_channel
        self.current_source_channel = current_source_channel

    def __str__(self):
        return f'{PSOC_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST},{self.sample_rate},{self.downsample},{self.gain_channel},{self.current_source_channel}{PSOC_TELEGRAM_END}'


# Error
PSOC_TELEGRAM__ERROR = f'{PSOC_TELEGRAM_TYPE_ERROR_RESPONSE}{PSOC_TELEGRAM_END}'
