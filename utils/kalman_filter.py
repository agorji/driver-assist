import time

import numpy as np


class KalmanFilter:
    DEFAULT_SPEED_ACCURACY = 2

    def __init__(self, acceleration_noise=2, location_noise=4, speed_noise=4):

        self.acceleration_noise = acceleration_noise

        self.measurement_cov_mat = np.array([[location_noise * location_noise, 0, location_noise * speed_noise, 0],
                                             [0, location_noise * location_noise, 0, location_noise * speed_noise],
                                             [location_noise * speed_noise, 0, speed_noise * speed_noise, 0],
                                             [0, location_noise * speed_noise, 0, speed_noise * speed_noise]])
        self.process_cov_mat = None

        self.measured_data = None
        self.predicted_data = None
        self.measured_cov_mat = None
        self.predicted_cov_mat = None
        self.previous_estimate_time = None
        self.kalman_gain = None

    def initialize(self, init_data, init_noise_vec, start_timestamp=None):
        if start_timestamp is not None:
            self.previous_estimate_time = start_timestamp
        else:
            self.previous_estimate_time = time.time()
        self.measured_data = init_data.copy()
        self.predicted_data = self.measured_data.copy()
        self.measured_cov_mat = np.array(
            [[init_noise_vec[0] * init_noise_vec[0], 0, init_noise_vec[0] * init_noise_vec[2], 0],
             [0, init_noise_vec[1] * init_noise_vec[1], 0, init_noise_vec[1] * init_noise_vec[3]],
             [init_noise_vec[0] * init_noise_vec[2], 0, init_noise_vec[2] * init_noise_vec[2], 0],
             [0, init_noise_vec[1] * init_noise_vec[3], 0, init_noise_vec[3] * init_noise_vec[3]],
             ])
        self.predicted_cov_mat = self.measured_cov_mat.copy()

    def predict_values(self, predict_time=None):
        if predict_time is None:
            predict_time = time.time()
        delta_t = predict_time - self.previous_estimate_time
        model_mat = np.array([[1, 0, delta_t, 0],
                              [0, 1, 0, delta_t],
                              [0, 0, 1, 0],
                              [0, 0, 0, 1]])
        self.predicted_data = model_mat @ self.measured_data

        pr_cv = np.array([delta_t * delta_t / 2 * self.acceleration_noise,
                          delta_t * delta_t / 2 * self.acceleration_noise,
                          delta_t * self.acceleration_noise,
                          delta_t * self.acceleration_noise])

        self.process_cov_mat = np.array([
            [pr_cv[0] * pr_cv[0], 0, pr_cv[0] * pr_cv[2], 0],
            [0, pr_cv[1] * pr_cv[1], 0, pr_cv[1] * pr_cv[3]],
            [pr_cv[0] * pr_cv[2], 0, pr_cv[2] * pr_cv[2], 0],
            [0, pr_cv[1] * pr_cv[3], 0, pr_cv[3] * pr_cv[3]],
        ])
        self.predicted_cov_mat = model_mat @ self.measured_cov_mat @ model_mat.T + self.process_cov_mat

    def update_estimations(self, new_data, measurement_noise=None, estimate_time=None):
        if estimate_time is None:
            estimate_time = time.time()
        self.predict_values(estimate_time)
        speed_included = len(new_data) == 4

        if speed_included:
            observation_mat = np.array([[1, 0, 0, 0],
                                        [0, 1, 0, 0],
                                        [0, 0, 1, 0],
                                        [0, 0, 0, 1]])
        else:
            observation_mat = np.array([[1, 0, 0, 0],
                                        [0, 1, 0, 0]])

        noise_included = measurement_noise is not None

        if noise_included:
            if measurement_noise[0] == 0:
                measurement_noise[0] = 0.001
            if speed_included:
                if measurement_noise[1] == 0:
                    measurement_noise[1] = 0.001
                self.measurement_cov_mat = np.array([
                    [measurement_noise[0] * measurement_noise[0], 0, 0, 0],
                    [0, measurement_noise[0] * measurement_noise[0], 0, 0],
                    [0, 0, measurement_noise[1] * measurement_noise[1], 0],
                    [0, 0, 0, measurement_noise[1] * measurement_noise[1]],
                ])
            else:
                measure_cov_len = len(self.measurement_cov_mat)
                if speed_included and measure_cov_len == 2:
                    prev_dist_err = self.measurement_cov_mat[0, 0]
                    self.measurement_cov_mat = np.array([
                        [prev_dist_err, 0, 0, 0],
                        [0, prev_dist_err, 0, 0],
                        [0, 0, self.DEFAULT_SPEED_ACCURACY * self.DEFAULT_SPEED_ACCURACY, 0],
                        [0, 0, 0, self.DEFAULT_SPEED_ACCURACY, self.DEFAULT_SPEED_ACCURACY]
                    ])
                elif not speed_included and measure_cov_len == 4:
                    self.measurement_cov_mat = self.measurement_cov_mat[:2, :2]

        self.kalman_gain = self.predicted_cov_mat @ observation_mat.T @ np.linalg.inv(
            observation_mat @ self.predicted_cov_mat @ observation_mat.T + self.measurement_cov_mat)
        self.measured_data = self.predicted_data + self.kalman_gain @ (new_data - observation_mat @ self.predicted_data)
        temp_mat = np.eye(3) - self.kalman_gain @ observation_mat
        self.measured_cov_mat = temp_mat @ self.predicted_cov_mat @ temp_mat.T + self.kalman_gain @ self.measurement_cov_mat @ self.kalman_gain.T

        self.previous_estimate_time = estimate_time

        self.predicted_data = self.measured_data.copy()
        self.predicted_cov_mat = self.measured_cov_mat.copy()
