NUMBER_OF_SWITCHES_PER_ROW = 3
NUMBER_OF_SWITCHES_PER_COLUMN = 3
NUMBER_OF_SWITCHES = 20
RATIO_OF_CACHING_NODES = 0.5
NUMBER_OF_HOSTS_PER_SWITCH = 1
NUMBER_OF_HOSTS = NUMBER_OF_SWITCHES * NUMBER_OF_HOSTS_PER_SWITCH
MOVE_EVENT_INTERVALS = 5
REQUEST_INTERVAL = 0.5
ALPHA_ZIPF = 1.1
MININET_IP = "0.0.0.0"
# MININET_IP = "192.168.57.3"
ITG_LOG_SERVER_IP = "127.0.0.1"
CONTROLLER_IP = "127.0.0.1"
CACHING_MODE_HOST = "LRU"
CACHING_MODE_SWITCH = "LRU"

FILE_REQUEST_LISTEN_PORT = 8511
HOST_AVAILABILITY_LISTEN_PORT = 8512
CACHING_STORAGE_PER_HOST = 50000
CACHING_STORAGE_PER_SWITCH = 200000

REPORT_INTERVAL = 100
NUMBER_OF_FILES = 1000
MEAN_FILE_SIZE_IN_KB = 10000

CACHE_ON_SWITCHES = True
CACHE_ON_HOST = True
GENERATE_TRAFFIC = True

ITG_SENDER_LOG_PATH = "ditgSenderLogs"
ITG_RECEIVER_LOG_PATH = "ditgReceiverLogs"

PRINT_LINK_CHANGES = False
PRINT_DUMMY_MESSAGES = False

USE_IPERF = True
ROUTE_SELECTION_ENERGY_AWARE = True

WEIGHT_ENERGY = 0.5
WEIGHT_CONNECTIVITY = 0.5
COST_CONTENT_SERVER = 0.2

WEIGHT_SELF_CAPACITY = 0.1
WEIGHT_NEIGHBOUR_CAPACITY = 0.2
WEIGHT_HOP_COUNT = 0.7

PARAMETER_DIVISION = 1
COST_START = 0.1
COST_CACHE_FILL = 0.1

# Constants

SOURCE_CONTENT_SERVER = 0
SOURCE_SWITCH = 1
SOURCE_HOST = 2
SOURCE_OWN_CACHE = 3
SOURCE_NOT_AVAILABLE = -1

DISABLE_MULTIPLE_REQUESTS_FROM_SAME_HOST = False
DATA_SCALING = 1

# SwitchMovement-------------------------------------

COORDINATE_LIMIT = 1000
AVERAGE_HEIGHT = 50
HEIGHT_DEVIATION = 1

RANDOM_SWITCH_MOVEMENT = False
FIGURE_8_SWITCH_MOVEMENT = True

FIGURE_8_ALPHA_VAR = 10
FIGURE_8_PERIOD = 60

# -------------------------------------

# LEVELS = { 'debug': logging.DEBUG,
#            'info': logging.INFO,
#            'output': OUTPUT,
#            'warning': logging.WARNING,
#            'error': logging.ERROR,
#            'critical': logging.CRITICAL }

MININET_LOG_LEVEL = 'output'

ONOS_INTENT_ADD_MODE = True
ONOS_LINK_ADD_MODE = True
