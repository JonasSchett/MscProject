import random


class Agent:
    """Agent class capable of playing a prisoners dilemma game with opponents"""

    def __init__(self, sim_data, location=(0, 0), social_value=0.1):
        self.neighbours = []
        self.actions = sim_data["actions"]
        # currently selected choice is initialised randomly to start
        self.selected_choice = random.choice(self.actions)
        # q value dictionary for each move
        self.Q_values = {}
        self.exploration_rate = sim_data["exploration_rate"]
        self.exploration_decay = sim_data["exploration_decay"]
        self.exploration_update = sim_data["exploration_update"]
        self.social_value = social_value
        self.played = False
        self.location = location
        self.social_adjustment = sim_data["social_adjustment"]
        self.beta = sim_data["social_step_size"]


        # current opponent of agent
        self.opponent = None

        # q values are initialised to 0
        for a in self.actions:
            self.Q_values[a] = 0.0

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

    def add_neighbours(self, neighbours):
        self.neighbours = self.neighbours + neighbours

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    def update_social_value(self):
        """Update social value based on actions of neighbours"""

        cooperating_neighbours = [x for x in self.neighbours if x.selected_choice == 'C']
        defecting_neighbours = [x for x in self.neighbours if x.selected_choice == 'D']

        # cooperation_rate is between -1 and 1
        cooperation_rate = (len(cooperating_neighbours) - len(defecting_neighbours)) / len(self.neighbours)

        # social adjustment has to be very low
        previous_part = (1 - self.social_adjustment) * self.social_value

        # social value is updated with cooperation rate
        new_part = self.social_adjustment * (self.social_value + self.beta * cooperation_rate)

        update_value = previous_part + new_part

        # cap update value between 0 and 1
        if update_value < 0:
            update_value = 0
        if update_value > 1:
            update_value = 1

        self.social_value = update_value

    # gain_reward and poll_action are closely coupled, they will be polled after one another
    # first, poll_action will yield an action and then gain_reward will get the reward
    # for that action later
    def gain_reward(self, reward, lr=0.1):
        # update q values based on the last selected_choice
        # and the reward here

        # cooperating neighbours are the neighbours that use cooperate
        cooperating_neighbours = [x for x in self.neighbours if x.selected_choice == 'C']

        # calculates the perceived value of the action based on neighbours (as described in paper)
        perceived_action_value = (len(cooperating_neighbours) * 1.0 / len(self.neighbours))
        if self.selected_choice is 'D':
            perceived_action_value = -perceived_action_value

        # total reward is based on perceived value and individual reward to agent
        total_reward = self.social_value * perceived_action_value + (1 - self.social_value) * reward

        # q values of this move are updated
        self.Q_values[self.selected_choice] = lr * total_reward + (1 - lr) * self.Q_values[self.selected_choice]

    def reset_played(self):
        """ resets the value of played"""
        self.played = False

    def poll_action(self):
        """ function to poll action of agent, agent will store action as it's last action for society to see"""
        self.played = True
        rand = random.uniform(0, 1)
        if self.exploration_update:
            self.exploration_rate *= self.exploration_decay
        if rand < self.exploration_rate:
            # explore random move
            self.selected_choice = random.choice(self.actions)
        else:
            # pick best action based on q values
            self.selected_choice = max(self.Q_values, key=self.Q_values.get)

        return self.selected_choice

    def set_opponent(self, opponent):
        """sets current opponent of agent"""
        self.opponent = opponent
