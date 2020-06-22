import random
import math
from Agent import Agent

class Society:
    """Society class hosting number of agents with set number of neighbours"""

    def __init__(self, num_agents=500, num_neighbours=20, social_value=0.1, learning_rate=0.1, width = 600, height = 600):
        self.agents = []
        self.lr = learning_rate
        # actions for prisoners dilemma
        actions = ['C', 'D']

        grid_size = int(math.ceil((1.0 * num_agents) ** 0.5))
        grid_step = 20
        size = grid_size * grid_step
        offset_x = width / 2 - size/2
        offset_y = height / 2 - size/2

        for i in range(num_agents):
            x_loc = (i % grid_size) * grid_step + offset_x
            y_loc = math.floor(1.0 * i / grid_size) * grid_step + offset_y
            self.agents.append(Agent(actions, social_value=social_value, location=(x_loc, y_loc), social_step_size=0.001))

        # assign neighbours to agent
        self.setup_neighbours_nearest(num_neighbours)

    def num_agents(self):
        return len(self.agents)

    def setup_neighbours_random(self, k):
        for agent in self.agents:
            agents_without_current = list(self.agents)
            agents_without_current.remove(agent)
            random_agents = random.choices(agents_without_current, k=k)
            agent.set_neighbours(random_agents)

    def setup_neighbours_nearest(self, k):
        """sets up the network in a way that every agent is connected to the k nearest other agents"""
        for agent in self.agents:
            agents_without_current = list(self.agents)
            agents_without_current.remove(agent)
            neighbours = []
            for i in range(k):
                closest_agent = None
                min_distance: int = 10000
                for neighbour in agents_without_current:
                    if not neighbour in neighbours:
                        distance = ((neighbour.location[0] - agent.location[0])**2 +
                                    (neighbour.location[1] - agent.location[1])**2)**0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_agent = neighbour
                if closest_agent:
                    neighbours.append( closest_agent)
            agent.set_neighbours(neighbours)
        pass

    def get_q_values(self):
        return [x.Q_values for x in self.agents]

    def get_social_values(self):
        return[x.social_value for x in self.agents]

    def play_game(self):
        """function to play individual games, games are not played at the same time. Agents use the last move played
        by their neighbours for deciding q values"""
        agent_to_play_1 = random.choice(self.agents)
        agent_to_play_2 = random.choice(agent_to_play_1.neighbours)
        action1 = agent_to_play_1.poll_action()
        action2 = agent_to_play_2.poll_action()

        if action1 == action2 == 'C':
            # both agents cooperated, give them rewards
            agent_to_play_2.gain_reward(3, self.lr)
            agent_to_play_1.gain_reward(3, self.lr)
        elif action1 == action2:
            # both agents defected
            agent_to_play_2.gain_reward(1, self.lr)
            agent_to_play_1.gain_reward(1, self.lr)
        elif action1 == 'D':
            # agent 1 defected, agent 2 cooperated
            agent_to_play_2.gain_reward(-1, self.lr)
            agent_to_play_1.gain_reward(5, self.lr)
        elif action2 == 'D':
            # agent 2 defected, agent 1 cooperated
            agent_to_play_2.gain_reward(5, self.lr)
            agent_to_play_1.gain_reward(-1, self.lr)
        else:
            print("Error happened in game")

        agent_to_play_2.update_social_value()
        agent_to_play_1.update_social_value()

    def play_all(self, iterations=1):
        """function to play a game at the same time for entire society. Agents are informed about moves of the
        neighbours that they took in the same iteration"""
        for i in range(iterations):
            for agent in self.agents:
                possible_opponents = [x for x in agent.neighbours if not x.played]
                if len(possible_opponents) is not 0:
                    opponent = random.choice(possible_opponents)
                    agent.set_opponent(opponent)
                    opponent.set_opponent(agent)
                    agent.poll_action()
                    opponent.poll_action()

            for agent in self.agents:
                agent.reset_played()
                agent_action = agent.selected_choice
                opponent_action = agent.opponent.selected_choice
                if agent_action == opponent_action == 'C':
                    agent.gain_reward(3, self.lr)
                elif agent_action == opponent_action:
                    agent.gain_reward(1, self.lr)
                elif agent_action == 'D':
                    agent.gain_reward(5, self.lr)
                elif agent_action == 'C':
                    agent.gain_reward(-1, self.lr)
                #agent.update_social_value()