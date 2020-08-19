import numpy as np
from Society import Society
from VisualisationScreen import VisualisationScreen
import matplotlib.pyplot as plt
import os
import argparse

# some global parameters for experimentation
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

# core parameters
num_agents = 500
num_neighbours = 20
learning_rate = 0.01

# main dictionary containing all simulation data
simulation_data = {
    # screen size options
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
    "exploration_rate": 1.0,
    "exploration_decay": 0.99,
}

confidence_intervals = {
    95: 1.96,
    99: 2.576,
    99.5: 2.807,
    99.9: 3.291
}


def main_experiment(games_per_iter, num_iter, exploration_update=False, social_update=False, play_successive=True,
                    experiment_name="default", experiment_dir="", social_values=None):
    """Main experiment for iterative prisoner's dilemma"""

    # simulation data is updated to use the update values specified in the function
    simulation_data["exploration_update"] = exploration_update
    simulation_data["update_social_values"] = social_update

    # the user can specify a list of social value orientations to be iterated which are used here
    if social_values is None:
        social_values = np.linspace(0, 1, 11)

    # the social_dict is a dictionary storing the results from each experiment for each social value
    social_dict = {}

    # all social value orientations specified are used here
    for soc in social_values:
        # the simulation data is updated to use the current social value orientation
        simulation_data["initial_social_value"] = soc

        # the following variables store data about the experiment which is used for creating the graphs
        average_coop = 0
        average_social = 0
        coop_rates = []
        updated_soc = []
        print('Social value currently operating:' + str(soc))
        # we are now iterating over all the specified iterations and create a new society for each
        for i in range(num_iter):
            s = Society(simulation_data)

            # each society plays the number of games specified
            # play successive is the main approach used for the project, play all was used for testing
            if play_successive:
                for j in range(games_per_iter):
                    s.play_game()
            else:
                s.play_all(games_per_iter)

            # calculations are performed to calculate the average cooperation rate, standard deviation, social values,
            # std deviation of updated social values and values required for producing the plots
            defect_established = 0
            coop_established = 0

            # here we iterate over the Q values of all agents in the society and count if they cooperate or defect
            for value in s.get_q_values():
                if value['C'] > value['D']:
                    coop_established += 1
                else:
                    defect_established += 1

            # in this next step the social value orientations of the society are retrieved and averaged
            social_values = s.get_social_values()
            # this variable is the average social value orientation within this iteration, there is another average
            # averaging over all iterations
            average_social_iter = 0.0
            for value in social_values:
                average_social_iter += value / len(social_values)

            # cooperation rate is calculated
            coop = coop_established / (coop_established + defect_established)

            coop_rates.append(coop)
            updated_soc.append(average_social_iter)

            # update outside averages
            average_coop += coop
            average_social += average_social_iter

        average_coop = average_coop * 1.0 / num_iter
        average_social = average_social * 1.0 / num_iter

        # the standard deviation and confidence values are calculated for this social value orientation
        # and added to the social_dict
        std_dev_coop = np.std(coop_rates)
        std_dev_soc = np.std(updated_soc)
        confidence_value_coop = confidence_intervals[99] * (std_dev_coop / (num_iter * 1.0) ** 0.5)
        confidence_value_soc = confidence_intervals[99] * (std_dev_soc / (num_iter * 1.0) ** 0.5)
        social_dict[soc] = (average_coop, average_social, confidence_value_coop, confidence_value_soc)

    # after all experiments are run, the data is prepared to be plotted
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

    # the filenames and folders are prepared for the experiment
    if exploration_update:
        experiment_name = experiment_name + "_exp"
    if social_update:
        experiment_name = experiment_name + "_soc"
    experiment_name += "_g" + str(games_per_iter) + "_i" + str(num_iter)

    if experiment_dir is not "":
        if not os.path.exists(experiment_dir):
            os.mkdir(experiment_dir)
        experiment_name = experiment_dir + "\\" + experiment_name

    # graphs are created
    create_graphs(coop_rate, social_values, indices, confidence_values_coop, confidence_values_soc, experiment_name)


def create_graphs(data, data2, indices, confidence_values, confidence_values_2, name):
    """Creates two graphs, one for the cooperation rate and one for the updated social value orientation"""

    # the defect rates are just those who do not cooperate and this is quickly calculated here
    defect_rates = [1 - x for x in data]


    width = 0.08

    # create plot for cooperation rates
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

    # store and clear the plot
    plt.savefig(name + '.png', dpi=300)
    plt.clf()

    # create plot for updated social values
    fig, ax = plt.subplots()
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    plt.bar(indices, data2, width, yerr=confidence_values_2)

    plt.ylabel('updated social value')
    plt.xlabel('initial social value')
    plt.title('updated social values')
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xticks(np.arange(0, 1.1, 0.1))

    # store and clear the plot
    plt.savefig(name + '_social_values.png', dpi=300)
    plt.clf()


def visual_experiment():
    """Default visual experiment, only run with either grid or scale free setup as
    it does not provide useful insight to random networks"""

    if simulation_data['grid_setup'] is False and simulation_data['scale_free_setup'] is False:
        simulation_data['grid_setup'] = True

    # society and visualisation screen are created, the visualisation screen then takes over the experiment
    s = Society(simulation_data)
    VisualisationScreen(s, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title="Visualisation", tick=0.1)


def experiment_set(games_per_iter=50000, num_iter=1000, results=""):
    """Full run of experiments described in project"""
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=True, social_update=True,
                    experiment_name="default", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=False, social_update=True,
                    experiment_name="default", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=True, social_update=False,
                    experiment_name="default", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=False, social_update=False,
                    experiment_name="default", experiment_dir=results)

    simulation_data["grid_setup"] = True
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=True, social_update=True,
                    experiment_name="grid", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=False, social_update=True,
                    experiment_name="grid", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=True, social_update=False,
                    experiment_name="grid", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=False, social_update=False,
                    experiment_name="grid", experiment_dir=results)
    #
    simulation_data["grid_setup"] = False
    simulation_data["scale_free_setup"] = True
    simulation_data["scale_free_links"] = 1
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=False, social_update=True,
                    experiment_name="scale", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=True, social_update=True,
                    experiment_name="scale", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=True, social_update=False,
                    experiment_name="scale", experiment_dir=results)
    main_experiment(games_per_iter=games_per_iter, num_iter=num_iter, exploration_update=False, social_update=False,
                    experiment_name="scale", experiment_dir=results)


def parse_arguments():
    """Function to parse arguments from the user, user arguments are optional and for more in depth experimentation
    it is recommended to use the dictionary above directly"""
    games = 50000
    iterations = 1000
    name = "experiment"
    directory = ""
    experiment = "single"

    parser = argparse.ArgumentParser(description="Social agent simulation software")
    parser.add_argument('--games', '-g', type=int, help="Games to be played per iteration")
    parser.add_argument('--iterations', '-i', type=int, help="Iterations to be simulated")
    parser.add_argument('--name', '-n', type=str, help="Specify the name of the experiment")
    parser.add_argument('--directory', '-d', type=str, help="directory for storing results (if specified)")
    parser.add_argument('--experiment', '-e', type=str,
                        help="Run a predefined set of experiments, possible arguments are: full, single, visual")
    parser.add_argument('--exploration_update', '-exp', type=bool,
                        help="Specify if the exploration rate should be updated")
    parser.add_argument('--social_update', '-soc', type=bool,
                        help="Specity if the social value orientation should be updated")
    parser.add_argument('--agents', '-a', type=int, help="Number of agents in society")
    parser.add_argument('--neighbours', '-ne', type=int, help="Number of neighbours per agent")
    parser.add_argument('--learning_rate', '-lr', type=float, help="Learning rate to be used")
    parser.add_argument('--exploration_rate', '-er', type=float, help="Initial exploration rate to be used")
    parser.add_argument('--network', '-net', type=str,
                        help="Type of network to be used other than random (scale, grid)")
    parser.add_argument('--exploration_decay', '-ed', type=float, help="Exploration decay to be used")
    parser.add_argument('--grid_size', '-gs', type=int, help="Grid size to be used if a grid experiment is run")
    parser.add_argument('--scale_free_links', '-sfl', type=int, help="Number of links created per added agent")
    parser.add_argument('--initial_social_value', '-isv', type=float, help="Initial social value orientation")
    parser.add_argument('--std_dev', '-std', type=float,
                        help="Standard deviation for setting up a normal distribution of social values")
    parser.add_argument('--random_social_value', '-rsv', type=bool,
                        help="Specify if random social value should be used (normal distribution)")
    parser.add_argument('--social_adjustment', '-sadj', type=float,
                        help="Social adjustment value to be used when updating social value orientation")
    parser.add_argument('--social_step_size', '-sss', type=float,
                        help="Social step size used when updating social value orientation")
    args = parser.parse_args()

    # transfer the commands to dictionary if they were specified, all commands are optional.
    if args.games is not None:
        games = args.games
    if args.iterations is not None:
        iterations = args.iterations
    if args.name is not None:
        name = args.name
    if args.directory is not None:
        directory = args.directory
    if args.experiment is not None and args.experiment in ['full', 'single', 'visual']:
        experiment = args.experiment
    if args.exploration_update is not None:
        simulation_data["exploration_update"] = args.exploration_update
    if args.social_update is not None:
        simulation_data["social_update"] = args.social_update
    if args.agents is not None:
        simulation_data["num_agents"] = args.agents
    if args.neighbours is not None:
        simulation_data["num_neighbours"] = args.neighbours
    if args.learning_rate is not None:
        simulation_data["learning_rate"] = args.learning_rate
    if args.exploration_rate is not None:
        simulation_data["exploration_rate"] = args.exploration_rate
    if args.network is not None and args.network in ['random', 'scale', 'grid']:
        if args.network == 'random':
            simulation_data['grid_setup'] = True
        elif args.network == 'scale':
            simulation_data['scale_free_setup'] = True
    if args.exploration_decay is not None:
        simulation_data["exploration_decay"] = args.exploration_decay
    if args.grid_size is not None:
        simulation_data["grid_size"] = args.grid_size
    if args.initial_social_value is not None:
        simulation_data["initial_social_value"] = args.initial_social_value
    if args.random_social_value is not None:
        simulation_data["random_social_value"] = args.random_social_value
    if args.std_dev is not None:
        simulation_data["std_dev"] = args.std_dev
    if args.social_adjustment is not None:
        simulation_data["social_adjustment"] = args.social_adjustment
    if args.social_step_size is not None:
        simulation_data["social_step_size"] = args.social_step_size

    return games, iterations, name, directory, experiment


def main():
    games, iterations, name, dictionary, experiment = parse_arguments()
    if experiment == 'single':
        main_experiment(games_per_iter=games, num_iter=iterations, experiment_name=name, experiment_dir=dictionary)
    elif experiment == 'visual':
        visual_experiment()
    elif experiment == 'full':
        experiment_set(games, iterations, dictionary)


if __name__ == '__main__':
    main()
