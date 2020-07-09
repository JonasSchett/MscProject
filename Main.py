import numpy as np
from Society import Society
from VisualisationScreen import VisualisationScreen
import matplotlib.pyplot as plt
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

num_agents = 500
num_neighbours = 20
learning_rate = 0.1

simulation_data_exp1 = {
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,
    "num_agents": num_agents,
    "learning_rate": learning_rate,
    "num_neighbours": num_neighbours,
    "update_social_values": False,
    "actions": ['C', 'D'],
    "grid_size": 20,
    "grid_setup": False,
    "exploration_rate": 0.9,
    "exploration_decay": 0.99,
    "exploration_update": False,
    "social_adjustment": 1,
    "social_step_size": 0.1,
}

simulation_data_exp2 = {
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,
    "num_agents": num_agents,
    "learning_rate": learning_rate,
    "num_neighbours": num_neighbours,
    "update_social_values": True,
    "actions": ['C', 'D'],
    "grid_size": 30,
    "grid_setup": True,
    "exploration_rate": 0.9,
    "exploration_decay": 0.99,
    "exploration_update": True,
    "social_adjustment": 0.01,
    "social_step_size": 1,
}


def first_experiment(games_per_iter, num_iter, exploration_update):
    # social values for an ireative run for values ranging from 0 to 1
    simulation_data_exp1["exploration_update"] = exploration_update
    social_values = np.linspace(0, 1, 11)
    social_dict = {}
    for soc in social_values:
        s = Society(soc, simulation_data_exp1)
        average_value = 0
        average_social = 0
        print('Social value currently operating:' + str(soc))
        for i in range(num_iter):
            s.play_all(games_per_iter)
            defect_established = 0
            coop_established = 0
            for value in s.get_q_values():
                if value['C'] > value['D']:
                    coop_established += 1
                else:
                    defect_established += 1
            social_values = s.get_social_values()
            for value in social_values:
                average_social += value / len(social_values)
            # coop established
            coop = coop_established / (coop_established + defect_established)
            average_value += coop
        average_value = average_value * 1.0 / num_iter
        average_social = average_social * 1.0 / num_iter
        social_dict[soc] = (average_value, average_social)

    indices = []
    coop_rate = []
    for key, value in social_dict.items():
        print(f'Initial social value: {key:.1f} cooperation rate: {value[0]:.4f} updated social value: {value[1]:.4f}')
        indices.append(key)
        coop_rate.append(value[0])
    defect_rates = [1-x for x in coop_rate]


    # show plot for visualisation
    width = 0.08
    p1 = plt.bar(indices, coop_rate, width, bottom=defect_rates)
    p2 = plt.bar(indices, defect_rates, width)

    plt.ylabel('cooperation percentage')
    plt.xlabel('initial social value (homogeneous society)')
    plt.title('cooperation rates')
    plt.yticks(np.arange(0,1.1,0.1))
    plt.xticks(np.arange(0,1.1,0.1))
    plt.legend((p1[0], p2[0]),('Coop', 'Defect'))
    plt.show()


def second_experiment():
    s = Society(0.7, simulation_data_exp2)
    screen = VisualisationScreen(s, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Experiment 2", tick=0.1)


if __name__ == '__main__':
    #first_experiment(games_per_iter=100, num_iter=10, exploration_update=False)
    #first_experiment(games_per_iter=100, num_iter=10, exploration_update=True)
    second_experiment()
