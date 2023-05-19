import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Perceptron import Perceptron
from SVM import SVM
from utils import *
import json


def optimize_perceptron(X, y, weights):
    A = weights[0]
    B = weights[1]
    C = weights[2]

    upper_points = X[y == 1]
    lower_points = X[y == -1]

    upper_distances = np.abs(
        A * upper_points[:, 0] + B * upper_points[:, 1] + C) / np.sqrt(A**2 + B**2)
    lower_distances = np.abs(
        A * lower_points[:, 0] + B * lower_points[:, 1] + C) / np.sqrt(A**2 + B**2)

    upper_points = upper_points[np.argsort(upper_distances)[:1]]
    lower_points = lower_points[np.argsort(lower_distances)[:2]]

    lower_midpoint = (lower_points[0] + lower_points[1]) / 2

    line_x = np.linspace(0, 1, 2)

    optimal_point = (upper_points[0] + lower_midpoint) / 2

    m = (lower_points[1][1] - lower_points[0][1]) / (lower_points[1][0] - lower_points[0][0])
    b = optimal_point[1] - m * optimal_point[0]

    line_y = m * line_x + b

    return line_y, upper_points, lower_points, optimal_point


def plot_preceptron(X, y, weights, epochs, l_rate):
    plt.clf()
    line_x = np.linspace(0, 1, 2)
    # w1*x1 + w2*x2 + b = 0 => -(w1*x1 + b)/w2 = x2
    line_y = -(line_x * weights[0] + weights[2])/weights[1]

    optimal_line_y, upper_points, lower_points, optimal_point = optimize_perceptron(
        X, y, weights)
    boundry_line_plt = plt.plot(line_x, line_y, color='blue')

    to_remove_idx = []
    for idx, point in enumerate(X):
        if point in upper_points or point in lower_points:
            to_remove_idx.append(idx)

    X = np.delete(X, to_remove_idx, axis=0)
    y = np.delete(y, to_remove_idx, axis=0)

    instances_plt = plt.scatter(X[:, 0], X[:, 1], color=[
        'red' if c == -1 else 'green' for c in y])

    optimal_point_plt = plt.scatter(
        optimal_point[0], optimal_point[1], color='black')
    lower_middle_point = (lower_points[0] + lower_points[1]) / 2
    middle_point_plt = plt.scatter(
        lower_middle_point[0], lower_middle_point[1], color='black')

    optimal_boundry_plt = plt.plot(
        line_x, optimal_line_y, color='purple', linestyle='dashed')
    select_up_plt = plt.scatter(
        upper_points[:, 0], upper_points[:, 1], color='purple')
    select_low_plt = plt.scatter(
        lower_points[:, 0], lower_points[:, 1], color='orange')

    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.title('Perceptron con ' + str(epochs) +
              ' epochs y learning rate ' + str(l_rate))
    plt.xlabel('x')
    plt.ylabel('y')

    # TODO: fix legend

    # plt.legend([boundry_line_plt, instances_plt, optimal_boundry_plt, optimal_point_plt, middle_point_plt],
    #            ['Decision boundary', 'Instances', 'Optimum', 'Optimum midway point', 'mid point'], loc='upper right')

    path = "out/perceptron/"+str(epochs)+"_epochs_" + \
        str(l_rate).replace("0.", "p") + "_lrate"

    plt.tight_layout()
    plt.savefig(path+'.png')


def plot_svm(X, y, r, weights, b, epochs, l_rate):
    plt.clf()
    line_x = np.linspace(0, 1, 2)

    # w1*x1 + w2*x2 + b = 0 => -(w1*x1 + b)/w2 = x2
    line_y = -(line_x * weights[0] + b)/weights[1]
    line_y_up = -(line_x * weights[0] + b + r)/weights[1]
    line_y_down = -(line_x * weights[0] + b - r)/weights[1]
    plt.scatter(X[:, 0], X[:, 1], color=[
                'red' if c == -1 else 'green' for c in y])
    plt.plot(line_x, line_y, color='black')
    # plt.plot(line_x, line_y_up, linestyle='dashed', color='blue')
    # plt.plot(line_x, line_y_down, linestyle='dashed', color='blue')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.legend(['Instance', 'Decision boundary', 'Margin'], loc='upper right')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('SVM con ' + str(epochs) +
              ' epochs y learning rate ' + str(l_rate))
    path = "out/svm/"+str(epochs)+"_epochs_" + \
        str(l_rate).replace("0.", "p") + "_lrate"
    plt.tight_layout()
    plt.savefig(path + '.png')


def run_perceptron(df, epochs, learning_rate):
    X = df.loc[:, ['x', 'y']].values
    y = df.loc[:, ['class']].values.ravel()

    perceptron = Perceptron(2)
    error, weights = perceptron.train(X, y, epochs, learning_rate)
    print("Perceptron:", weights)
    plot_preceptron(X, y, weights, epochs, learning_rate)


def run_svm(df, max_c, c_rate, test_pctg, epochs=1000, learning_rate=0.01):
    c_precisions = []
    for c in range(1, max_c, c_rate):
        precisions = []
        partitions = partition_dataset(df, test_pctg)
        for idx, partition in enumerate(partitions):
            test = partition
            train = pd.concat([df for df in partitions if df is not partition])

            train_X = train.loc[:, ['x', 'y']].values
            train_y = train.loc[:, ['class']].values.ravel()

            svm = SVM(2)
            error, weights, b = svm.train(
                train_X, train_y, c, learning_rate, epochs)

            test_X = test.loc[:, ['x', 'y']].values
            test_y = test.loc[:, ['class']].values.ravel()

            correct = 0
            for idx, x in enumerate(test_X):
                prediction = svm.predict(weights, b, x)
                if prediction == test_y[idx]:
                    correct += 1

            precisions.append(correct / len(test_X))
        c_precisions.append(
            {"mean": np.mean(precisions), "std": np.std(precisions)})

    optimal_c = np.argmax([c["mean"] for c in c_precisions]) + 1

    X = df.loc[:, ['x', 'y']].values
    y = df.loc[:, ['class']].values.ravel()
    svm = SVM(2)
    min_error, best_weights, best_b = svm.train(
        X, y, optimal_c, learning_rate, epochs)
    print("SVM best weights and error:", best_weights, min_error)
    r = svm.calculate_margin(best_weights)

    print("SVM:", best_weights)
    print("Margin:", r)

    plot_svm(X, y, r, best_weights, best_b, epochs, learning_rate)


if __name__ == '__main__':

    with open("config.json") as config_file:
        config = json.load(config_file)
        generate = config["generate"] if "generate" in config else True
        file_name = config["file_name"] if "file_name" in config else "TP3-1"
        method = config["method"] if "method" in config else "SVM"
        point_amount = config["point_amount"] if "point_amount" in config else 30
        epochs = config["epochs"] if "epochs" in config else 1000
        learning_rate = config["learning_rate"] if "learning_rate" in config else 0.01

        x_min, x_max, y_min, y_max = 0, 1, 0, 1

        if generate:
            data, line = random_points_within_range(
                x_min, x_max, y_min, y_max, point_amount)
            df = pd.DataFrame(data, columns=["x", "y", "class"])
            df.to_csv(file_name+".csv", index=False)
            line_df = pd.DataFrame([line], columns=["m", "b"])
            line_df.to_csv(file_name+"-line.csv", index=False)
        else:
            df = pd.read_csv(file_name+".csv")
            line = pd.read_csv(file_name+"-line.csv").values

        print(method, epochs, learning_rate)

        if method.lower() == "perceptron":
            run_perceptron(df, epochs, learning_rate)
        elif method.lower() == "svm":
            test_pctg = 0.1
            max_c = 250
            c_rate = 50

            run_svm(df, max_c, c_rate, test_pctg, epochs, learning_rate)
        else:
            print("Invalid method")
    config_file.close()