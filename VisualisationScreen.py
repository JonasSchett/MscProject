import arcade
from Society import Society

class VisualisationScreen:
    def __init__(self, society, width=600, height=600):
        self.width = width
        self.height = height
        self.society = society

    def draw(self):
        arcade.open_window(self.width, self.height, "Example")
        arcade.set_background_color(arcade.color.WHITE)
        arcade.start_render()
        locations = []
        fully_drawn_agents = []
        for agent in self.society.agents:
            fully_drawn_agents.append(agent)
            locations.append(agent.location)
            for neighbour in agent.neighbours:
                if neighbour not in fully_drawn_agents:
                    arcade.draw_line(agent.location[0], agent.location[1], neighbour.location[0], neighbour.location[1],
                                     arcade.color.DARK_CYAN, 1)


        arcade.draw_points(locations,arcade.color.BLACK,5)
        arcade.finish_render()
