import bisect
import math
import traceback
from random import randint

import numpy as np

import settings as s


def rss_to_data_rate(rss):
    min_sensitivity = [
        (-82.1, 0),
        (-82, 6),
        (-81, 9),
        (-79, 12),
        (-77, 18),
        (-74, 24),
        (-70, 36),
        (-66, 48),
        (-65, 54),
    ]
    satisfied_min_value = bisect.bisect_left(min_sensitivity, (rss,))
    if satisfied_min_value >= len(min_sensitivity):
        satisfied_min_value = len(min_sensitivity) - 1
    return min_sensitivity[satisfied_min_value][1]


class DroneMover(object):
    initial_drone_positions = []
    drone_positions = []
    host_positions = []
    drone2drone_distances = []
    drone2host_distances = []
    neighbors = {}
    drone2drone_link_capacities = []
    drone2host_link_capacities = []
    drone2host_link_capacities_previous = []
    num_of_drones_initial = 0
    num_of_drones_alive = 0
    operating_drones = []
    active_link_pair_capacity_table = []
    previous_link_pair_capacity_table = []

    def __init__(self, drone_number=s.NUM_OF_DRONES):
        # drone_positions = np.random.randint(low=0, high=COORDINATE_LIMIT, size=(drone_number, 2))
        # drone2drone_distances = np.array([complex(c.m_x, c.m_y) for c in cells])
        self.num_of_drones_alive = drone_number
        self.num_of_drones_initial = drone_number
        self.operating_drones = np.arange(drone_number)
        self.grid_initialization()
        self.drone_positions = np.array(self.initial_drone_positions)
        self.host_positions = np.array(self.initial_drone_positions)
        self.host_positions[:, 2] = 0
        if s.FIGURE_8_DRONE_MOVEMENT:
            self.initialCircularPhase = np.random.uniform(low=-np.pi, high=np.pi, size=(s.NUM_OF_DRONES, 1))
            self.move_drones_figure8(0)
        self.drone2drone_distances = np.zeros(shape=(s.NUM_OF_DRONES, s.NUM_OF_DRONES))
        self.drone2host_distances = self.drone_positions[:, 2]
        self.drone2drone_link_capacities = np.full_like(self.drone2drone_distances, 0)
        self.drone2host_link_capacities = np.full_like(self.drone2host_distances, 0)
        self.get_distances()
        self.get_link_capacities()
        # self.select_links()

    def grid_initialization(self):
        initial_drone_positions = []
        effective_area_x = s.COORDINATE_LIMIT_X[1] - s.COORDINATE_LIMIT_X[0]
        effective_area_y = s.COORDINATE_LIMIT_Y[1] - s.COORDINATE_LIMIT_Y[0]
        row_distance = effective_area_x / (s.NUM_OF_DRONES_PER_ROW + 1)
        column_distance = effective_area_y / (s.NUM_OF_DRONES_PER_COLUMN + 1)

        for i in range(s.NUM_OF_DRONES_PER_ROW):
            for j in range(s.NUM_OF_DRONES_PER_COLUMN):
                initial_drone_positions.append(
                    [s.COORDINATE_LIMIT_X[0] + row_distance * (i + 1),
                     s.COORDINATE_LIMIT_Y[0] + column_distance * (j + 1),
                     randint(s.AVERAGE_HEIGHT - s.HEIGHT_DEVIATION, s.AVERAGE_HEIGHT + s.HEIGHT_DEVIATION)])
        self.initial_drone_positions = np.array(initial_drone_positions)

    def get_drone_positions(self):
        return self.drone_positions

    def select_links(self, max_link_number=3):
        linking_drones = []
        connected_drones = []
        candidate_links = []
        self.active_link_pair_capacity_table = []
        self.neighbors.clear()
        for drone in self.operating_drones:
            self.neighbors[drone] = []
        if self.num_of_drones_alive < 2:
            print("One drone is left")
            return
        temp_drone2drone_link_capacities = np.copy(self.drone2drone_link_capacities)
        connected_drones.append(self.content_server_drone_id)
        link_number = max_link_number
        while link_number > 0:
            linking_drones = np.argpartition(self.drone2drone_link_capacities[self.content_server_drone_id],
                                             -link_number)[
                             -link_number:].astype(int).tolist()
            if self.drone2drone_link_capacities[self.content_server_drone_id, linking_drones[0]] <= 0:
                # Content server drone does not have links to connect, decrement link number for this server
                link_number -= 1
                linking_drones = [self.content_server_drone_id]
            else:
                linking_drones.reverse()
                self.neighbors[self.content_server_drone_id] = linking_drones[:]
                break

        for drone in linking_drones:
            temp_pair = [self.content_server_drone_id, drone]
            temp_pair.sort()
            temp_pair.append(int(self.drone2drone_link_capacities[self.content_server_drone_id, drone]))
            self.active_link_pair_capacity_table.append(temp_pair)
            self.neighbors[drone] = [self.content_server_drone_id]
        # Add closest neighbors
        connected_drones = connected_drones + linking_drones
        # Eliminate content_server_drone_id from capacity matrix, it has max link number
        temp_drone2drone_link_capacities[:, self.content_server_drone_id] = -1

        capacity_matrix_for_linking_drones = np.array(
            [temp_drone2drone_link_capacities[i] for i in linking_drones])
        # for drone in connected_drones:
        #     capacity_matrix_for_linking_drones[:, drone] = -1
        try:
            # Obtain minimum spanning tree
            while len(connected_drones) != self.num_of_drones_alive:
                closest_drone_index = np.argmax(capacity_matrix_for_linking_drones)
                new_drone = int(closest_drone_index % self.num_of_drones_initial)
                source_drone_index = closest_drone_index / self.num_of_drones_initial
                if capacity_matrix_for_linking_drones[source_drone_index, new_drone] <= 0:
                    break
                source_drone = linking_drones[source_drone_index]
                temp_pair = [source_drone, new_drone]
                temp_pair.sort()
                temp_pair.append(int(self.drone2drone_link_capacities[source_drone, new_drone]))
                # Prevent arg_max to get the same value
                capacity_matrix_for_linking_drones[source_drone_index, new_drone] = -1
                if source_drone == new_drone:
                    continue
                if new_drone in linking_drones:
                    new_drone_index = linking_drones.index(new_drone)
                    capacity_matrix_for_linking_drones[new_drone_index, source_drone] = -1
                temp_drone2drone_link_capacities[new_drone, source_drone] = -1
                if new_drone not in connected_drones:
                    self.neighbors[source_drone].append(new_drone)
                    # Create a list and add the first element
                    self.neighbors[new_drone] = [source_drone]
                    self.active_link_pair_capacity_table.append(temp_pair)
                    if len(self.neighbors[source_drone]) == max_link_number:
                        capacity_matrix_for_linking_drones = np.delete(capacity_matrix_for_linking_drones,
                                                                       source_drone_index, 0)
                        linking_drones.remove(source_drone)
                        temp_drone2drone_link_capacities[:, source_drone] = -1
                        capacity_matrix_for_linking_drones[:, source_drone] = -1
                    # Eliminate already connected drones from the new drone's row on the capacity list
                    # temp_drone2drone_link_capacities[new_drone, connected_drones] = -1
                    # Add new drone's neighbors to the search list
                    connected_drones.append(new_drone)
                    linking_drones.append(new_drone)
                    capacity_matrix_for_linking_drones = np.vstack((capacity_matrix_for_linking_drones,
                                                                    temp_drone2drone_link_capacities[new_drone]))
                else:
                    candidate_links.append(temp_pair)
            if len(connected_drones) != self.num_of_drones_alive:
                # Disconnected graph
                print("Disconnected graph")
                for drone in self.operating_drones:
                    if drone not in connected_drones:
                        linking_drones.append(drone)
                        capacity_matrix_for_linking_drones = np.vstack((capacity_matrix_for_linking_drones,
                                                                        temp_drone2drone_link_capacities[drone]))

            # Add extra links from candidates
            while len(linking_drones) > 1 and len(candidate_links):
                temp_pair = candidate_links.pop(0)
                if len(self.neighbors[temp_pair[0]]) != max_link_number and len(
                        self.neighbors[temp_pair[1]]) != max_link_number:
                    self.neighbors[temp_pair[0]].append(temp_pair[1])
                    self.neighbors[temp_pair[1]].append(temp_pair[0])
                    self.active_link_pair_capacity_table.append(temp_pair)
                    if len(self.neighbors[temp_pair[0]]) == max_link_number:
                        new_drone_index = linking_drones.index(temp_pair[0])
                        capacity_matrix_for_linking_drones = np.delete(capacity_matrix_for_linking_drones,
                                                                       new_drone_index, 0)
                        capacity_matrix_for_linking_drones[:, temp_pair[0]] = -1
                        linking_drones.remove(temp_pair[0])
                        # Update source_drone_index
                    if len(self.neighbors[temp_pair[1]]) == max_link_number:
                        source_drone_index = linking_drones.index(temp_pair[1])
                        capacity_matrix_for_linking_drones = np.delete(capacity_matrix_for_linking_drones,
                                                                       source_drone_index, 0)
                        capacity_matrix_for_linking_drones[:, temp_pair[1]] = -1
                        linking_drones.remove(temp_pair[1])
            # Add extra links
            while len(linking_drones) > 1 and np.amax(capacity_matrix_for_linking_drones) > 0:
                closest_drone_index = np.argmax(capacity_matrix_for_linking_drones)
                new_drone = int(closest_drone_index % self.num_of_drones_initial)
                source_drone_index = closest_drone_index / self.num_of_drones_initial
                source_drone = linking_drones[source_drone_index]
                new_drone_index = linking_drones.index(new_drone)
                self.neighbors[source_drone].append(new_drone)
                self.neighbors[new_drone].append(source_drone)
                if source_drone == new_drone:
                    break
                temp_pair = [source_drone, new_drone]
                temp_pair.sort()
                link_capacity = int(self.drone2drone_link_capacities[source_drone, new_drone])
                if link_capacity <= 0:
                    print("Error here")
                temp_pair.append(link_capacity)
                self.active_link_pair_capacity_table.append(temp_pair)
                # Prevent arg_max to get the same value
                capacity_matrix_for_linking_drones[source_drone_index, new_drone] = -1
                capacity_matrix_for_linking_drones[new_drone_index, source_drone] = -1
                if len(self.neighbors[new_drone]) == max_link_number:
                    capacity_matrix_for_linking_drones = np.delete(capacity_matrix_for_linking_drones,
                                                                   new_drone_index, 0)
                    capacity_matrix_for_linking_drones[:, new_drone] = -1
                    linking_drones.remove(new_drone)
                    # Update source_drone_index
                    source_drone_index = linking_drones.index(source_drone)
                if len(self.neighbors[source_drone]) == max_link_number:
                    capacity_matrix_for_linking_drones = np.delete(capacity_matrix_for_linking_drones,
                                                                   source_drone_index, 0)
                    capacity_matrix_for_linking_drones[:, source_drone] = -1
                    linking_drones.remove(source_drone)
        except Exception as e:
            print("Link establishment error:")
            print(traceback.format_exc())
            print(e)
        # with open('links.txt', 'w+') as f:
        #     f.write('\n'.join('{} {}'.format(node[0], node[1]) for node in self.active_link_pair_capacity_table))
        # print(self.active_link_pair_capacity_table)

    def print_links_to_file(self, file_name=None):
        if file_name is None:
            file_name = "links.txt"
        with open(file_name, 'w+') as f:
            f.write('\n'.join('{} {}'.format(node[0], node[1]) for node in self.active_link_pair_capacity_table))

    def get_drone2drone_distances(self):
        for i in range(s.NUM_OF_DRONES):
            for j in range(s.NUM_OF_DRONES):
                self.drone2drone_distances[i, j] = np.sqrt(
                    np.sum((self.drone_positions[i] - self.drone_positions[j]) ** 2, axis=0)) if i != j else np.inf

    def get_drone2host_distances(self):
        for i in range(s.NUM_OF_DRONES):
            self.drone2host_distances[i] = np.sqrt(
                np.sum((self.drone_positions[i] - self.host_positions[i]) ** 2, axis=0))

    def get_distances(self):
        self.get_drone2drone_distances()
        self.get_drone2host_distances()

    def get_drone2drone_link_capacities(self):
        try:
            for i, j in np.ndindex(self.drone2drone_distances.shape):
                # P_r(dB) = P_t(dB) + G(dB) - 10 * a * log10(d) - L_FS
                # Transmission power P_t=20dBm, Power gains factor G=-6dBi, U2U pathloss coefficient a=2
                # L_FS = 10 * a  log(f) + 20 log( 4 * pi / c ) = 40dB for f=2.4GHz and a=2
                # Pr(dB) = P_r(dB) - 20*log10(d)
                # SNR(dB) = P_r(dB) - No(dB) * f  Noise variance No=-96dBm or -84
                # SNR(dB) = 58 - 20*log10(d)
                # shannon_capacity = BW * log2(1+SNR)
                distance = self.drone2drone_distances[i, j]
                if i not in self.operating_drones or j not in self.operating_drones:
                    # One of the drones is not operating
                    self.drone2drone_link_capacities[i, j] = -3
                    continue
                if distance == np.inf:
                    self.drone2drone_link_capacities[i, j] = -2
                    continue
                elif distance > 500:
                    self.drone2drone_link_capacities[i, j] = -1
                    continue
                snr = 58 - 20 * math.log10(distance)
                shannon_capacity = 10 * math.log(1 + 10 ** (snr / 10))
                self.drone2drone_link_capacities[i, j] = shannon_capacity
        except Exception as e:
            print(e)

    # def getDroneToDroneLinkCapacities():
    #     try:
    #         for i, j in np.ndindex(drone2drone_distances.shape):
    #             # P_r(dB) = P_t(dB) + G(dB) - 10 * a * log10(4 * pi / lambda ) - 10 * a * log10(d)
    #             # Transmission power P_t=20dBm, Power gains factor G=-31.5dB, U2U pathloss coefficient a=2.6
    #             # L_FS = 10 * a  log(f) + 20 log( 4 * pi / c ) = 40dB for f=2.4GHz and a=2.6
    #             # Pr(dB) = P_r(dB) - 20*log10(d)
    #
    #             distance = drone2drone_distances[i, j]
    #             if distance == -1:
    #                 drone2drone_link_capacities[i, j] = 0
    #                 continue
    #             rss = -22 - 26 * math.log10(distance)
    #             drone2drone_link_capacities[i, j] = rssToDataRate(rss)
    #     except Exception as e:
    #         print(e)

    def get_drone2host_link_capacities(self):
        try:
            for i in range(self.drone2host_distances.shape[0]):
                # Probability LoS: pr_los = 1 / ( 1 + a * exp(-b * (elevation_angle - a)) )
                # U2I channel parameter a=12 and b=0.135
                # elevation_angle = sin^-1(h / distance)
                # Free space address loss: pl_fs = 10 * a  log(f) + 20 log( 4 * pi / c ) = 32.44dB for f=1GHz,
                # 40dB for f=2.4GHz
                # pl_los  = pl_fs + 20*log10(d) + n_los
                # pl_nlos = pl_fs + 20*log10(d) + n_nlos
                # n_LoS=1 and n_NLoS=20 are additional attenuation factors due to the LoS and NLoS
                # pl_avg = pl_los * pr_los + pl_nlos * (1-pr_los)
                # p_t=20dBm
                a = 12
                b = 0.135
                pl_fs = 40
                p_t = 20
                distance = self.drone2host_distances[i]
                height = self.drone_positions[i][2]
                elevation_angle = math.asin(height / distance)
                path_loss = pl_fs + 20 * math.log10(distance)
                pr_los = 1 / (1 + 12 * math.exp(-b * (elevation_angle - a)))
                pl_los = path_loss  # +0
                pl_nlos = pl_fs + 20 * math.log10(distance) + 13.01
                pl_avg = pl_los * pr_los + pl_nlos * (1 - pr_los)
                rss = p_t - pl_avg
                snr = rss + 84
                shannon_capacity = 10 * math.log(1 + 10 ** (snr / 10))
                self.drone2host_link_capacities[i] = shannon_capacity
        except Exception as e:
            print(e)

    def get_link_capacities(self):
        self.get_drone2drone_link_capacities()
        self.get_drone2host_link_capacities()

    def store_previous_link_capacities(self):
        self.drone2host_link_capacities_previous = np.copy(self.drone2host_link_capacities)
        self.previous_link_pair_capacity_table = self.active_link_pair_capacity_table[:]

    def move_drones_random(self):
        movements = np.random.randint(low=-1, high=2, size=(s.NUM_OF_DRONES, 3))
        self.drone_positions = np.add(self.drone_positions, movements)

    def move_drones_figure8(self, current_time):
        t = 2 * np.pi * current_time / s.FIGURE_8_PERIOD + self.initialCircularPhase
        x_delta = s.FIGURE_8_ALPHA_VAR * np.sqrt(2) * np.cos(t) / (np.sin(t) ** 2 + 1)
        y_delta = s.FIGURE_8_ALPHA_VAR * np.sqrt(2) * np.cos(t) * np.sin(t) / (np.sin(t) ** 2 + 1)
        z_delta = np.random.randint(low=-1, high=2, size=(s.NUM_OF_DRONES, 1))
        movements = np.concatenate((x_delta, y_delta, z_delta), axis=1)
        movements = np.rint(movements).astype(int)
        self.drone_positions = np.add(self.drone_positions, movements)

    def move_drones_for_one_time_interval(self, current_time=0):
        if s.RANDOM_DRONE_MOVEMENT:
            self.move_drones_random()
        if s.FIGURE_8_DRONE_MOVEMENT:
            self.move_drones_figure8(current_time)
        # Prevent drones go out zone
        np.clip(self.drone_positions[:, 0], *s.COORDINATE_LIMIT_X, out=self.drone_positions[:, 0])
        np.clip(self.drone_positions[:, 1], *s.COORDINATE_LIMIT_Y, out=self.drone_positions[:, 1])
        # print(self.drone_positions)
        # print("**********")
        self.get_distances()
        self.store_previous_link_capacities()
        self.get_link_capacities()
        # self.select_links()
        # print("----------")


if __name__ == '__main__':
    droneMover = DroneMover()
    droneMover.move_drones_for_one_time_interval()
    pass
