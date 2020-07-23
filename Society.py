import random
import math
import numpy as np
from Agent import Agent


def scale_free_neighbour_location_setup(agent, radius, base_orientation):
    theta_range = np.arange(base_orientation, base_orientation+ 2 * math.pi, 2 * math.pi / len(agent.neighbours))
    # initially, we position the agent
    unpositioned_neighbours = [x for x in agent.neighbours if x.location[0] is 0 and x.location[1] is 0]
    if len(unpositioned_neighbours) is 0:
        return

    thetas = np.zeros(len(unpositioned_neighbours))
    calculation_radii = np.zeros(len(unpositioned_neighbours))
    for i in range(len(unpositioned_neighbours)):
        # theta is the interpolation between 0 and 2*pi
        thetas[i] = theta_range[i]
        calculation_radius = radius * len(unpositioned_neighbours[i].neighbours)/len(agent.neighbours)
        calculation_radii[i] = calculation_radius
        x = agent.location[0] + calculation_radius * math.sin(thetas[i])
        y = agent.location[1] + calculation_radius * math.cos(thetas[i])
        neighbour: Agent = unpositioned_neighbours[i]
        neighbour.location = (x, y)

    for i in range(len(unpositioned_neighbours)):
        scale_free_neighbour_location_setup(unpositioned_neighbours[i], calculation_radii[i]*0.8, thetas[i])



class Society:
    """Society class hosting number of agents with set number of neighbours"""

    def __init__(self, sim_data):
        self.sim_data = sim_data
        self.agents = []
        self.lr = sim_data["learning_rate"]
        self.num_agents = sim_data["num_agents"]
        self.update_social_values = sim_data["update_social_values"]

        # actions for prisoners dilemma
        self.actions = sim_data["actions"]
        self.social_value = sim_data["initial_social_value"]
        self.grid_size = int(math.ceil((1.0 * self.num_agents) ** 0.5))
        self.grid_step = 20
        size = self.grid_size * self.grid_step
        self.width = sim_data["width"]
        self.height = sim_data["height"]
        self.offset_x = self.width / 2 - size / 2
        self.offset_y = self.height / 2 - size / 2

        if sim_data['grid_setup']:
            self.setup_agents_grid(sim_data["grid_size"])
        elif sim_data['scale_free_setup']:
            self.setup_neighbours_ba()
            agent_neighbour_buckets = {}
            for agent in self.agents:
                neighbours = len(agent.neighbours)
                if neighbours in agent_neighbour_buckets:
                    agent_neighbour_buckets[neighbours] += 1
                else:
                    agent_neighbour_buckets[neighbours] = 1
            for i in range(max(agent_neighbour_buckets.keys()) + 1):
                pass
                # num_agents = (agent_neighbour_buckets[i] if i in agent_neighbour_buckets else 0)
                # print("neighbours: " + str(i) + " agents: " + str(num_agents))
        else:
            self.setup_neighbours_random(sim_data["num_neighbours"])

    def setup_agents_grid(self, square):
        self.grid_step = 20
        size = square * self.grid_step
        self.offset_x = self.width / 2 - size / 2
        self.offset_y = self.height / 2 - size / 2

        self.agents = []
        for y in range(square):
            for x in range(square):
                self.agents.append(
                    Agent(self.sim_data, (self.grid_step * x + self.offset_x, self.grid_step * y + self.offset_y),
                          self.social_value))

        for y in range(square):
            for x in range(square):
                agent = self.agents[y * square + x]
                neighbour1 = self.agents[(y + 1) * square + x] if y < square - 1 else None
                neighbour2 = self.agents[y * square + (x + 1)] if x < square - 1 else None
                if neighbour1 is not None:
                    self.set_neighbours(agent, neighbour1)
                if neighbour2 is not None:
                    self.set_neighbours(agent, neighbour2)

    @staticmethod
    def set_neighbours(agent1: Agent, agent2: Agent):
        agent1.add_neighbour(agent2)
        agent2.add_neighbour(agent1)

    def num_agents(self):
        return len(self.agents)

    def setup_neighbours_ba(self):
        self.agents = []

        # initiate first agent
        for i in range(self.num_agents):
            agent = Agent(self.sim_data, social_value=self.social_value)

            # add neighbours from already existing agents:
            if len(self.agents) > 0:
                # create grade
                agents_roulette_wheel = []
                sum_of_grades: float = 0
                for a in self.agents:
                    sum_of_grades += len(a.neighbours)

                for a in self.agents:
                    agent_grade: float = len(a.neighbours)
                    agent_probability: float = agent_grade / sum_of_grades if sum_of_grades is not 0 else 1
                    agents_roulette_wheel.append((agent_probability, a))
                agents_roulette_wheel.sort(reverse=True, key=lambda x: x[0])

                # create random number and select agent:
                random_challenge = 0
                # random number for selecting agent
                number = random.uniform(0, 1)
                for (p, a) in agents_roulette_wheel:
                    # need to select an agent where the random number is within its bracket
                    # the bracket is defined by the random challenge (lower bound)
                    # and the random challenge + its probability
                    random_challenge += p
                    if number < random_challenge:
                        # add agent connection
                        a.add_neighbour(agent)
                        agent.add_neighbour(a)
                        break
            # add new agents to list
            self.agents.append(agent)
        # after connecting the agents we need to place them onto the grid in a nice way to visualise the scale free network
        # sort agents by number of neighbours they have
        self.agents.sort(key=lambda x: len(x.neighbours), reverse=True)
        # take first agent and set it to be the centre:
        core: Agent = self.agents[0]
        core.location = (self.sim_data['width'] / 2, self.sim_data['height'] / 2)

        scale_free_neighbour_location_setup(core, self.sim_data['width']/1.7, 0)

        # average overall position of all agents to centre of screen
        average_pos = (0,0)
        for agent in self.agents:
            average_pos = np.add(average_pos, agent.location)
        average_pos = np.divide(average_pos, len(self.agents))
        centre = (self.sim_data['width']/2, self.sim_data['height']/2)
        offset = np.subtract(centre,average_pos)
        # adjust all agents' positions
        for agent in self.agents:
            agent.location = np.add(agent.location, offset)

    def setup_neighbours_random(self, num_neighbours):
        self.agents = []
        for i in range(self.num_agents):
            x_loc = (i % self.grid_size) * self.grid_step + self.offset_x
            y_loc = math.floor(1.0 * i / self.grid_size) * self.grid_step + self.offset_y
            self.agents.append(
                Agent(self.sim_data, (x_loc, y_loc), self.social_value))

        for agent in self.agents:
            # create new neighbours for agent, need to ensure that the neighbours are not added twice
            agents_without_current = [x for x in self.agents if x is not agent]

            random_agents = random.choices(agents_without_current, k=num_neighbours)
            agent.set_neighbours(random_agents)

    def setup_neighbours_random_no_double(self, k):
        self.agents = []
        for i in range(self.num_agents):
            x_loc = (i % self.grid_size) * self.grid_step + self.offset_x
            y_loc = math.floor(1.0 * i / self.grid_size) * self.grid_step + self.offset_y
            self.agents.append(Agent(self.actions, social_value=self.social_value, location=(x_loc, y_loc)))

        for agent in self.agents:
            # create new neighbours for agent, need to ensure that the neighbours are not added twice
            agents_without_current = [x for x in self.agents if x not in agent.neighbours]
            agents_without_current.remove(agent)

            random_agents = random.choices(agents_without_current, k=k - len(agent.neighbours))
            agent.set_neighbours(random_agents)
            for neighbour in random_agents:
                neighbour.add_neighbour(agent)

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
                        distance = ((neighbour.location[0] - agent.location[0]) ** 2 +
                                    (neighbour.location[1] - agent.location[1]) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            closest_agent = neighbour
                if closest_agent:
                    neighbours.append(closest_agent)
            agent.set_neighbours(neighbours)
        pass

    def get_q_values(self):
        return [x.Q_values for x in self.agents]

    def get_social_values(self):
        return [x.social_value for x in self.agents]

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
        if self.sim_data['update_social_values']:
            agent_to_play_2.update_social_value()
            agent_to_play_1.update_social_value()

    def play_all(self, iterations=1, verbose=False):
        """function to play a game at the same time for entire society. Agents are informed about moves of the
        neighbours that they took in the same iteration"""
        for i in range(iterations):
            if verbose and (i+1) % 1000 is 0:
                print('iteration: '+str(i))
            for agent in self.agents:
                possible_opponents = [x for x in agent.neighbours if not x.played]
                if len(possible_opponents) is not 0:
                    opponent = random.choice(possible_opponents)
                    agent.set_opponent(opponent)
                    opponent.set_opponent(agent)
                    agent.poll_action()
                    opponent.poll_action()

            for agent in self.agents:
                if agent.opponent is not None:
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
                    if self.update_social_values:
                        agent.update_social_value()
