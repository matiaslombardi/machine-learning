import math
import numpy as np
import random

class Kmeans:
    def __init__(self, k, observations, genres):
        self.k = k
        self.observations = observations
        # TODO: check
        self.genres_per_cluster = [{genre: 0 for genre in genres} for _ in k]

    def check_centroids(self, centroids, new_centroids):
        return np.array_equal(centroids, new_centroids)

    def get_centroids(self, clusters):
        # TODO: check si esta bien lo de la ultima posicion. Esta el -1 porque hay que sacarle el genero
        new_centroids = np.zeros(shape=(self.k, len(self.observations[0]) - 1))
        for cluster in clusters:
            ######
            # TODO: check!!!!!!!!
            masked_cluster = [subarray[:-1] for subarray in clusters[cluster]]
            ######
            new_centroids[cluster] = np.mean(masked_cluster, axis=0) 
        return new_centroids

    def fill_clusters(self, centroids):
        clusters = {cat: [] for cat in np.arange(self.k)}
        # clusters = {cat: {"genre": "", "values":[]} for cat in np.arange(self.k)}
        
        for observation in self.observations:
            min_dist = math.inf
            cluster_idx = None

            obs_array = np.array(observation)

            for idx, centroid in enumerate(centroids):
                # print("Observation: " + str(observation), "Centroid: " + str(centroid))
                centroid = np.array(centroid)
                # TODO: check si esta bien lo de la ultima posicion
                dist = np.linalg.norm(obs_array[:-1] - centroid)

                if dist < min_dist:
                    min_dist = dist
                    cluster_idx = idx
            clusters[cluster_idx].append(observation)
        return clusters

    # TODO: capaz aca pasarle el k para reutilizar las pruebas
    def solve(self, genres):
        # TODO: se supone que observations es un df? Aca elegimos de forma random

        # TODO: check si esta bien lo de la ultima posicion
        centroids = random.sample(self.observations, self.k)[:-1]
        clusters = self.fill_clusters(centroids)

        new_centroids = self.get_centroids(clusters)

        while not np.array_equal(centroids, new_centroids):
            centroids = new_centroids
            self.fill_clusters(centroids)
            new_centroids = self.get_centroids(clusters)
        
    

        for i, cluster in enumerate(clusters):
            for observation in cluster:
                self.genres_per_cluster[i][observation[-1]] += 1

        return new_centroids, clusters

    def predict_genre(self, observation, centroids):
        cluster_idx = -1
        for idx, centroid in enumerate(centroids):
            # print("Observation: " + str(observation), "Centroid: " + str(centroid))
            centroid = np.array(centroid)
            # TODO: check si esta bien lo de la ultima posicion
            dist = np.linalg.norm(observation[:-1] - centroid)

            if dist < min_dist:
                min_dist = dist
                cluster_idx = idx
        
        # TODO: check!!!!!!!
        return max(self.genres_per_cluster[cluster_idx], key=self.genres_per_cluster[cluster_idx].get)

    def calculate_variation(self, clusters):
        total_variation = 0
        for cluster in clusters.values():
            cluster_variation = 0
            for i, obs_i in enumerate(cluster):
                for j, obs_j in enumerate(cluster):
                    # TODO: check si esta bien lo de la ultima posicion
                    cluster_variation += np.sum((np.array(obs_i[:-1]) - np.array(obs_j[:-1]))**2)
            
            total_variation += cluster_variation / len(cluster)
        return total_variation
