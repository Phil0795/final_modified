import time
# PC-Arduino protocol
# Pubilc
ARDUINO_TELEGRAM_END = '\r\n'
ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_REQUEST = "00"
ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE = "01"
ARDUINO_TELEGRAM_TYPE_PROGRESS_CONTROL_REQUEST = "02"
ARDUINO_TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE = "03"
ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST = "04"
ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE = "05"
ARDUINO_TELEGRAM_TYPE_ERROR_RESPONSE = "99"

# Launch test
ARDUINO_TELEGRAM_LAUNCH_TEST_REQUEST = f'{ARDUINO_TELEGRAM_TYPE_LAUNCH_TEST_REQUEST}{ARDUINO_TELEGRAM_END}'.encode(
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


# Set parameter
class ARDUINO_TELEGRAM_SET_PARAMETER_REQUEST:
    def __init__(self, bending_direction, bending_speed, cycles, steps):

        self.bending_direction = bending_direction
        self.bending_speed = bending_speed
        self.cycles = cycles
        self.steps = steps

    def __str__(self):
        return f'{ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST},{self.bending_direction},{self.bending_speed},{self.cycles},{self.steps}{ARDUINO_TELEGRAM_END}'


class ARDUINO_TELEGRAM_SET_PARAMETER_RESPONSE:
    def __init__(self, bending_direction, bending_speed, cycles, steps):
        ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST
        self.bending_direction = bending_direction
        self.bending_speed = bending_speed
        self.cycles = cycles
        self.steps = steps

    def __str__(self):
        return f'{ARDUINO_TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE},{self.bending_direction},{self.bending_speed},{self.cycles},{self.steps}{ARDUINO_TELEGRAM_END}'


# Error
ARDUINO_TELEGRAM__ERROR = f'{ARDUINO_TELEGRAM_TYPE_ERROR_RESPONSE}{ARDUINO_TELEGRAM_END}'

# Function
# def send_launch_test_request(serial, timeout=1):
#     serial.write(ARDUINO_TELEGRAM_LAUNCH_TEST_REQUEST)
#     send_successful = False
#     time_start = time.time()
#     while not send_successful:
#         response = serial.read_until(expected=serial.LF).decode('UTF-8')
#         if response == ARDUINO_TELEGRAM_LAUNCH_TEST_RESPONSE:
#             send_successful = True


# def send_test_progress_control_request(serial, progress):
#     if progress == 0:
#         serial.write(ARDUINO_TELEGRAM_STOP_TEST_REQUEST)
#     elif progress == 1:
#         serial.write(ARDUINO_TELEGRAM_START_TEST_REQUEST)
#     elif progress == 2:
#         serial.write(ARDUINO_TELEGRAM_PAUSE_TEST_REQUEST)


# def send_test_set_parameter_request(serial, bending_direction, bending_speed, cycles):
#     serial.write(bytes(str(ARDUINO_TELEGRAM_SET_PARAMETER_REQUEST(
#         bending_direction=bending_direction, bending_speed=bending_speed, cycles=cycles)), 'UTF-8'))


# PSoC
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
    def __init__(self, sample_rate, downsample, reference_channel):
        self.sample_rate = sample_rate
        self.downsample = downsample
        self.reference_channel = reference_channel

    def __str__(self):
        return f'{PSOC_TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST},{self.sample_rate},{self.downsample},{self.reference_channel}{PSOC_TELEGRAM_END}'


# Error
PSOC_TELEGRAM__ERROR = f'{PSOC_TELEGRAM_TYPE_ERROR_RESPONSE}{PSOC_TELEGRAM_END}'
