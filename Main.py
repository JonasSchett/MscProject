import numpy as np
from Society import Society
from VisualisationScreen import VisualisationScreen
import time

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

num_agents = 500
num_neighbours = 4
learning_rate = 0.1


def first_experiment():
    # social values for an ireative run for values ranging from 0 to 1
    social_values = np.linspace(0, 1, 11)
    social_dict = {}
    for soc in social_values:
        s = Society(num_agents, num_neighbours, social_value=soc, learning_rate=learning_rate,
                    width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        #screen = VisualisationScreen(s, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        #screen.draw()
        average_value = 0
        average_social = 0
        print('Social value currently operating:' + str(soc))
        for i in range(10):
            s.play_all(100)
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
        average_value = average_value * 1.0 / 10
        average_social = average_social * 1.0 / 10
        social_dict[soc] = (average_value, average_social)

    for value in social_dict.items():
        print(value)


def second_experiment():
    # social values for an ireative run for values ranging from 0 to 1

    s = Society(num_agents, num_neighbours, 0.7, learning_rate=learning_rate,
                width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

    screen = VisualisationScreen(s, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Experiment 2", tick=0.01)


if __name__ == '__main__':
    second_experiment()
