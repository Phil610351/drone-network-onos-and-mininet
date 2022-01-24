import glob
import logging
import pickle

from tabulate import tabulate

from actors.Task import Status

file_list = {
    "Adaptive": "/home/onur/Coding/projects/sdnCaching/results/request_interval/adaptive",
    "Aggressive": "/home/onur/Coding/projects/sdnCaching/results/request_interval/aggressive",
    "Aggressive-Wait": "/home/onur/Coding/projects/sdnCaching/results/request_interval/aggressive-wait",
}


def read_pickle_file(filename):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)


def get_multiple_files(files):
    data_obtained = {}

    for group_name, group_path in files.items():
        data_obtained[group_name] = {}
        list_of_folders = glob.glob(group_path + "/*")
        for folder_path in list_of_folders:
            folder_name = folder_path.split("/")[-1]
            data_obtained[group_name][folder_name] = []
            list_of_files = glob.glob(folder_path + "/*")
            for file_path in list_of_files:
                data_obtained[group_name][folder_name].append(read_pickle_file(file_path))
    return data_obtained


def get_specific_tasks(results, assignment_method, subsection_name):
    adaptive5_results = results[assignment_method][subsection_name]
    tasks = []
    for result in adaptive5_results:
        tasks.extend(result["tasks"])
    return tasks


def get_total_penalty(tasks):
    total_penalty = 0
    for task in tasks:
        total_penalty += task.get_prioritized_penalty()
    return total_penalty


def get_average_system_times(tasks):
    total_delay = 0
    total_pool_time = 0
    total_tx_time = 0
    total_queue_time = 0
    total_process_time = 0
    task_counter = 0
    for task in tasks:
        if task.status not in [Status.COMPLETED, Status.PROCESSING]:
            task_counter += 1
            pool_time = task.tx_start_time - task.start_time
            tx_time = task.tx_end_time - task.start_time
            queue_time = task.process_start_time - task.tx_end_time
            process_time = task.process_end_time - task.process_start_time
            total_pool_time += pool_time
            total_tx_time += tx_time
            total_queue_time += queue_time
            total_process_time += process_time
            total_delay += task.end_time - task.start_time
    averages = {
        "average_delay": total_delay / task_counter,
        "average_pool_time": total_pool_time / task_counter,
        "average_tx_time": total_tx_time / task_counter,
        "average_queue_time": total_queue_time / task_counter,
        "average_process_time": total_process_time / task_counter,
    }
    return averages


def get_average_penalty(tasks):
    total_penalty = get_total_penalty(tasks)
    average_penalty = total_penalty / len(tasks)
    return average_penalty


def get_ratio_of_failed_tasks(tasks):
    task_counter = 0
    for task in tasks:
        if task.status not in [Status.COMPLETED, Status.PROCESSING]:
            task_counter += 1

    return task_counter / len(tasks)


def get_ratio_of_tasks_assigned_to_cloud(tasks):
    task_counter = 0
    for task in tasks:
        if task.is_assigned_to_cloud:
            task_counter += 1
    return task_counter / len(tasks)


def get_category_delays(results):
    headers = ["Method-Category", "Average Penalty", "Task Failure Ratio", "Cloud Ratio"]
    rows = []
    for method_name, method_data in results.items():
        for category, category_results in method_data.items():
            tasks = get_specific_tasks(results, method_name, category)
            avg_penalty = get_average_penalty(tasks)
            ratio_of_failed_tasks = get_ratio_of_failed_tasks(tasks)
            ratio_of_tasks_assigned_to_cloud = get_ratio_of_tasks_assigned_to_cloud(tasks)

            rows.append([f"{method_name}-{category}", f"{avg_penalty:.2f}", f"{ratio_of_failed_tasks:.3f}",
                         f"{ratio_of_tasks_assigned_to_cloud:.3f}"])

    logging.info(f'\n{tabulate(rows, headers, tablefmt="pretty", stralign="left")}')


if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, "INFO"), format="%(asctime)s %(levelname)s -> %(message)s")

    result_data = get_multiple_files(file_list)
    # print(result_data)
    get_category_delays(result_data)
    pass
    # adaptive5_tasks = get_specific_tasks(result_data, "Adaptive", "5")
    # print(adaptive5_tasks)
