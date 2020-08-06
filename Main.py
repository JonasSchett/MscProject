from typing import Dict, List, Any, Union

import numpy as np
from Society import Society
from VisualisationScreen import VisualisationScreen
import matplotlib.pyplot as plt

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1500

num_agents = 500
num_neighbours = 20
learning_rate = 0.1

simulation_data: Dict[Union[str, Any], Union[Union[int, float, bool, List[str]], Any]] = {
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,

    # Society options
    "num_agents": num_agents,
    "learning_rate": learning_rate,
    "num_neighbours": num_neighbours,

    # Social value oriented values
    "update_social_values": False,
    "random_social_value": False,
    "std_dev": 0.1,
    "initial_social_value": 0.7,
    "social_adjustment": 1,
    "social_step_size": 0.1,

    # actions in game of prisoners dilemma
    "actions": ['C', 'D'],

    # network setup options
    "grid_size": 20,
    "grid_setup": False,
    "scale_free_setup": False,
    "scale_free_links": 1,

    # exploration setup options
    "exploration_update": False,
    "exploration_rate": 0.9,
    "exploration_decay": 0.9999,
}

confidence_intervals = {
    95: 1.96,
    99: 2.576,
    99.5: 2.807,
    99.9: 3.291
}


def first_experiment(games_per_iter, num_iter, exploration_update, social_update, play_successive=True, experiment_name="default", social_values=None):
    # social values for an ireative run for values ranging from 0 to 1
    simulation_data["exploration_update"] = exploration_update
    simulation_data["update_social_values"] = social_update
    if social_values is None:
        social_values = np.linspace(0, 1, 11)
    social_dict = {}
    for soc in social_values:
        simulation_data["initial_social_value"] = soc
        average_value = 0
        average_social = 0
        coop_rates = []
        updated_soc = []
        print('Social value currently operating:' + str(soc))
        for i in range(num_iter):
            s = Society(simulation_data)

            if play_successive:
                for j in range(games_per_iter):
                    s.play_game()
            else:
                s.play_all(games_per_iter)

            defect_established = 0
            coop_established = 0
            for value in s.get_q_values():
                if value['C'] > value['D']:
                    coop_established += 1
                else:
                    defect_established += 1
            social_values = s.get_social_values()
            average_social_iter = 0.0
            for value in social_values:
                average_social_iter += value/len(social_values)
            # coop established
            coop = coop_established / (coop_established + defect_established)
            coop_rates.append(coop)
            updated_soc.append(average_social_iter)
            average_value += coop
            average_social += average_social_iter

        average_value = average_value * 1.0 / num_iter
        average_social = average_social * 1.0 / num_iter
        std_dev_coop = np.std(coop_rates)
        std_dev_soc = np.std(updated_soc)
        confidence_value_coop = confidence_intervals[99] * (std_dev_coop/(num_iter*1.0)**0.5)
        confidence_value_soc = confidence_intervals[99] * (std_dev_soc/(num_iter*1.0)**0.5)
        social_dict[soc] = (average_value, average_social, confidence_value_coop, confidence_value_soc)

    indices = []
    coop_rate = []

    social_values = []
    confidence_values_coop = []
    confidence_values_soc = []
    for key, value in social_dict.items():
        print(f'Initial social value: {key:.1f} cooperation rate: {value[0]:.4f}+-{value[2]:.4f} updated social value:'
              f' {value[1]:.4f}+-{value[3]:.4f}')
        indices.append(key)
        coop_rate.append(value[0])
        confidence_values_coop.append(value[2])
        social_values.append(value[1])
        confidence_values_soc.append(value[3])

    if exploration_update:
        experiment_name = experiment_name + "_exp"
    if social_update:
        experiment_name = experiment_name + "_soc"
    experiment_name += "_g" + str(games_per_iter) + "_i" + str(num_iter)
    create_graphs(coop_rate, social_values, indices, confidence_values_coop, confidence_values_soc, experiment_name)


def create_graphs(data, data2, indices, confidence_values, confidence_values_2, name):
    defect_rates = [1 - x for x in data]
    # show plot for cooperation rates
    width = 0.08

    fig, ax = plt.subplots()
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    p1 = plt.bar(indices, data, width, yerr=confidence_values)
    p2 = plt.bar(indices, defect_rates, width, bottom=data)

    plt.ylabel('cooperation percentage')

    plt.xlabel('initial social value')
    plt.title('cooperation rates')
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xticks(np.arange(0, 1.1, 0.1))
    plt.legend((p1[0], p2[0]), ('Coop', 'Defect'), loc="lower right")

    plt.savefig(name + '.png', dpi=300)
    plt.clf()
    #show plot for updated social values
    fig, ax = plt.subplots()
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    p1 = plt.bar(indices, data2, width, yerr=confidence_values_2)

    plt.ylabel('updated social value')

    plt.xlabel('initial social value')
    plt.title('updated social values')
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xticks(np.arange(0, 1.1, 0.1))

    plt.savefig(name + '_social_values.png', dpi=300)
    plt.clf()

def second_experiment():
    simulation_data["grid_setup"] = True
    s = Society(simulation_data)
    screen = VisualisationScreen(s, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Experiment 2", tick=0.1)


def third_experiment():
    simulation_data["scale_free_setup"] = True
    s = Society(simulation_data)
    screen = VisualisationScreen(s, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Experiment 3", tick=0.1)

def experiment_set_two():
    first_experiment(games_per_iter=50000, num_iter=10, exploration_update=True, social_update=True,
                     experiment_name="default")
    first_experiment(games_per_iter=50000, num_iter=10, exploration_update=False, social_update=True,
                     experiment_name="default")
    first_experiment(games_per_iter=50000, num_iter=10, exploration_update=True, social_update=False,
                     experiment_name="default")
    first_experiment(games_per_iter=50000, num_iter=10, exploration_update=False, social_update=False,
                     experiment_name="default")

    # simulation_data["grid_setup"] = True
    #
    # first_experiment(games_per_iter=50000, num_iter=1000, exploration_update=True, social_update=True,
    #                  experiment_name="grid")
    # first_experiment(games_per_iter=50000, num_iter=1000, exploration_update=False, social_update=True,
    #                  experiment_name="grid")
    # first_experiment(games_per_iter=50000, num_iter=1000, exploration_update=True, social_update=False,
    #                  experiment_name="grid)
    # first_experiment(games_per_iter=50000, num_iter=1000, exploration_update=False, social_update=False,
    #                  experiment_name="grid")
    #
    # simulation_data["grid_setup"] = False
    # simulation_data["scale_free_setup"] = True
    # simulation_data["scale_free_links"] = 1
    # first_experiment(games_per_iter=50000, num_iter=5, exploration_update=False, social_update=True,
    #                  experiment_name="scale")
    # first_experiment(games_per_iter=50000, num_iter=5, exploration_update=True, social_update=True,
    #                  experiment_name="scale")
    # first_experiment(games_per_iter=50000, num_iter=5, exploration_update=True, social_update=False,
    #                  experiment_name="scale")
    # first_experiment(games_per_iter=50000, num_iter=5, exploration_update=False, social_update=False,
    #                  experiment_name="scale")

    # simulation_data['scale_free_links'] = 3
    # first_experiment(games_per_iter=10000, num_iter=1000, exploration_update=False, social_update=True,
    #                  experiment_name="scale3")
    # first_experiment(games_per_iter=10000, num_iter=1000, exploration_update=True, social_update=True,
    #                  experiment_name="scale3")
    # first_experiment(games_per_iter=10000, num_iter=1000, exploration_update=True, social_update=False,
    #                  experiment_name="scale3")
    # first_experiment(games_per_iter=10000, num_iter=1000, exploration_update=False, social_update=False,
    #                  experiment_name="scale3")

if __name__ == '__main__':
    #experiment_set_one()
    #experiment_set_two()
    #experiment_set_two()
    # simulation_data["scale_free_setup"] = True
    first_experiment(games_per_iter=50000, num_iter=1000, exploration_update=True, social_update=True, experiment_name="default4")
    #first_experiment(games_per_iter=1000, num_iter=10, exploration_update=False, social_update=False)
    #second_experiment()
    #third_experiment()