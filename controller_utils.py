import json
import logging

import requests

from network_utils import host_ip_to_mac
from settings import CONTROLLER_IP, LOG_LEVEL

LINK_CONFIGURATION_PATH = "/onos/v1/network/configuration/links/"
NETWORK_CONFIGURATION_PATH = "/onos/v1/network/configuration"
DISTANCE_ESTIMATION_PATH = "/onos/v1/paths/{}/{}"
INTENTS_PATH = "/onos/v1/intents"
METRICS_PATH = "/onos/cpman/controlmetrics/messages"
URL_TEMPLATE = "http://{}:8181{}"

LINK_CONFIGURATION_URL = URL_TEMPLATE.format(CONTROLLER_IP, LINK_CONFIGURATION_PATH)
NETWORK_CONFIGURATION_URL = URL_TEMPLATE.format(CONTROLLER_IP, NETWORK_CONFIGURATION_PATH)
DISTANCE_ESTIMATION_URL = URL_TEMPLATE.format(CONTROLLER_IP, DISTANCE_ESTIMATION_PATH)
INTENTS_URL = URL_TEMPLATE.format(CONTROLLER_IP, INTENTS_PATH)
METRICS_URL = URL_TEMPLATE.format(CONTROLLER_IP, METRICS_PATH)

BASIC_AUTH_HEADERS = {
    'Authorization': "Basic b25vczpyb2Nrcw==",
}

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(levelname)s -> %(message)s")
logging.getLogger()


def escape_path(path):
    return path.replace(":", "%3A").replace("/", "%2F")


def get_distance_and_switches_passed(src, dst):
    switches_passed = []

    if src.startswith("of"):  # Source is switch
        # src_id = urllib2.quote('of:0000000000000001')
        src_id = escape_path(src)
    else:
        src_mac = host_ip_to_mac(src)
        src_id = escape_path(src_mac) + '%2FNone'

    dst_mac = host_ip_to_mac(dst)
    dst_id = escape_path(dst_mac) + '%2FNone'
    link = DISTANCE_ESTIMATION_URL.format(src_id, dst_id)
    response = requests.request("GET", link, headers=BASIC_AUTH_HEADERS)
    data = json.loads(response.text)["paths"][0]
    distance = data["cost"]
    for hop in data["links"]:
        if "device" in hop["dst"]:
            next_node = hop["dst"]["device"]
            switches_passed.append(next_node)
    return distance, switches_passed


def get_distance(src_of_name, dst_of_name):
    try:
        link = DISTANCE_ESTIMATION_URL.format(src_of_name, dst_of_name)
        response = requests.request("GET", link, headers=BASIC_AUTH_HEADERS)
        data = json.loads(response.text)
        if "paths" not in data or len(data["paths"]) == 0:
            return
        data = data["paths"][0]
        distance = int(data["cost"])
    except Exception as e:
        logging.error(e)
        return
    return distance


def delete_link(link):
    url = LINK_CONFIGURATION_URL + escape_path(link)
    response = requests.request("DELETE", url,
                                headers=BASIC_AUTH_HEADERS)
    logging.debug(response.text)


def post_link(payload):
    response = requests.request("POST", LINK_CONFIGURATION_URL, data=json.dumps(payload),
                                headers=BASIC_AUTH_HEADERS)
    logging.debug(response.text)


def get_network_configurations():
    response = requests.request("GET", NETWORK_CONFIGURATION_URL, headers=BASIC_AUTH_HEADERS)
    current_info = json.loads(response.text)
    return current_info


def post_network_configurations(payload):
    response = requests.request("POST", NETWORK_CONFIGURATION_URL, data=json.dumps(payload),
                                headers=BASIC_AUTH_HEADERS)
    logging.debug("RESPONSE post_network_configurations: %s" % response)


def get_intents():
    response = requests.request("GET", INTENTS_URL, headers=BASIC_AUTH_HEADERS)
    current_info = json.loads(response.text)
    return current_info


def post_intent(intent):
    logging.debug(requests.request("POST", INTENTS_URL, data=json.dumps(intent), headers=BASIC_AUTH_HEADERS))


def delete_intent(intent_key):
    url = "{}/org.onosproject.ovsdb/{}".format(INTENTS_URL, intent_key)
    logging.debug(requests.request("DELETE", url, headers=BASIC_AUTH_HEADERS))


def get_metrics():
    response = requests.request("GET", METRICS_URL, headers=BASIC_AUTH_HEADERS)
    current_info = json.loads(response.text)
    return current_info


if __name__ == '__main__':
    logging.info(get_network_configurations())
    logging.info(get_distance_and_switches_passed("of:1000000000000002", "10.0.0.3"))
