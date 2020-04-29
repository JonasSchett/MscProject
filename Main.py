import numpy as np
from Society import Society

num_agents = 500
num_neighbours = 20
learning_rate = 0.1

if __name__ == '__main__':
    # social values for an ireative run for values ranging from 0 to 1
    social_values = np.linspace(0, 1, 11)
    social_dict = {}
    for soc in social_values:
        s = Society(num_agents, num_neighbours, social_value=soc, learning_rate=learning_rate)
        average_value = 0
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
            # coop established
            coop = coop_established / (coop_established + defect_established)
            average_value += coop
        average_value = average_value * 1.0 / 10
        social_dict[soc] = average_value

    for value in social_dict.items():
        print(value)