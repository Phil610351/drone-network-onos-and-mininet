import logging
import time

import settings as s


class Simulation:
    simulation_id = str(int(time.time() // 10))
    current_time = 0
    end_time = s.SIMULATION_DURATION
    drone_id_close_to_bs = None
    controller_host = None
    bs_host = None
    nat_host = None
    nat_host_ip = None
    cloud_server = None
    cloud_server_ip = None
    task_assigner_host = None
    task_assigner_host_ip = None
    task_organizer = None
    task_generator = None
    all_vehicles = {}
    connecting_vehicles = {}
    tasks = []
    events = {}
    upload_reports = {}
    number_of_reassigned_tasks = 0
    settings = None
    real_life_start_time = time.strftime('%m%d_%H%M')
    results_file_name = None
    record_file_name = None
    cloud_iperf_process = None
    record = None
    old_record = None

    @staticmethod
    def set_task_assigner(host):
        Simulation.task_assigner_host_ip = host.intfs[0].ip
        logging.info("Task assigner host name: %s ,ip: %s" % (host.name, Simulation.task_assigner_host_ip))
        Simulation.task_assigner_host = host

    @staticmethod
    def set_nat_host(host):
        Simulation.nat_host_ip = host.intfs[0].ip
        logging.info("NAT host name: %s ,ip: %s" % (host.name, Simulation.nat_host_ip))
        Simulation.nat_host = host

    @staticmethod
    def set_cloud_server(host):
        Simulation.cloud_server_ip = host.intfs[0].ip
        logging.info("Cloud_server name: %s ,ip: %s" % (host.name, Simulation.cloud_server_ip))
        Simulation.cloud_server = host
