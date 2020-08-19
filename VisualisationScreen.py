import arcade

class VisualisationScreen(arcade.Window):
    """Visualisationscreen class is used for visualising agent societies"""
    def __init__(self, society, width=600, height=600, title="Enter title", tick=1, print_tick=1):
        super().__init__(width, height, title)

        # initialises variables
        self.width = width
        self.height = height
        self.society = society
        self.connection_drawn = False
        self.tick = tick
        self.print_tick = print_tick
        self.time_elapsed = 0
        self.print_time_elapsed = 0

        # here we set the background of our window and start the simulation, which will repeatedly
        # poll on_draw and on_update
        arcade.set_background_color(arcade.color.WHITE)
        arcade.run()

    def on_draw(self):
        """In this function, the agents are drawn to the screen using their location, links are drawn as lines between
        agents and their neighbours"""

        arcade.start_render()

        # the agents are drawn one by one, but agents that are already fully drawn wont be drawn again to save
        # frames during the simulation
        fully_drawn_agents = []
        for agent in self.society.agents:
            fully_drawn_agents.append(agent)
            for neighbour in agent.neighbours:
                if neighbour not in fully_drawn_agents:
                    arcade.draw_line(agent.location[0], agent.location[1], neighbour.location[0], neighbour.location[1],
                                     arcade.color.DARK_CYAN, 1)

        # defecting agents are separated from cooperating agents
        defecting_agent_locations = [x.location for x in self.society.agents if x.selected_choice == 'D']
        cooperating_agent_locations = [x.location for x in self.society.agents if x.selected_choice == 'C']

        # points of different colour are drawn for defecting and cooperating agents
        arcade.draw_points(defecting_agent_locations, arcade.color.RED, 5)
        arcade.draw_points(cooperating_agent_locations, arcade.color.GREEN, 5)

    def on_update(self, delta_time: float):
        """This method is called at fixed time intervals by the arcade library and polls the society to play games"""
        self.time_elapsed += delta_time
        self.print_time_elapsed += delta_time

        # after a fixed time interval, the society will be polled to play 100 games
        if self.time_elapsed > self.tick:
            self.time_elapsed = 0
            if self.society is not None:
                self.society.play_all(100)

        # after a different fixed time interval cooperation values are printed to the screen
        if self.print_time_elapsed > self.print_tick:
            self.print_time_elapsed = 0
            social_value_average = 0
            defecting = len([x for x in self.society.agents if x.selected_choice == 'D'])
            cooperating = len([x for x in self.society.agents if x.selected_choice == 'C'])
            for agent in self.society.agents:
                social_value_average += agent.social_value

            # data is prepared and finally printed to the console
            defect_established = 0
            coop_established = 0
            for value in self.society.get_q_values():
                if value['C'] > value['D']:
                    coop_established += 1
                else:
                    defect_established += 1
            # coop established
            coop_rate = coop_established / (coop_established + defect_established)

            social_value_average /= len(self.society.agents)
            print(f'Social value average: {social_value_average:.2f} Agents defecting: {defecting} Agents cooperating: {cooperating} Cooperation Rate: {coop_rate:.2f}')

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """This method had to be implemented as the class extends the window provided by arcade, but nothing happens"""
        pass
