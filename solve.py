#!/usr/bin/env python3
import z3

class WrongColour(Exception):
    """ Means that this colour isn't in the set of avilable colours """
    pass

def btoi(b):
    """ converts a z3 bool to a z3 int """
    return z3.If(b, z3.IntVal(1), z3.IntVal(0))

def sumbools(bs):
    """ counts the number of true bools in a list of z3 bools """
    return z3.Sum(*[btoi(b) for b in bs])

class GameSolver:
    """ Among Us game state solver. Takes in what knowledge you provide it, finds all possible solutions
    to a system of equations that models this knowledge, the important game mechanics, and which players
    are the impostors. Can provide a count map of the numer of models for which each player is an
    impostor """
    def __init__(self, n_players, n_impostors):
        """ Construct a GameSolver with a known number of players and number of impostors """
        self.n_players = n_players
        # Some variables that model the state of each player
        self.alive, self.murdered, self.impostor, self.ejected = (
            [z3.Bool('%s-%d' % (varname, player_id)) for player_id in range(self.n_players)]
            for varname in [
                'player-is-alive'
                ,'player-was-murdered'
                ,'player-is-impostor'
                ,'player-was-ejected'
            ]
        )

        # First bit of information known is the number of impostors
        self.n_impostors = z3.IntVal(n_impostors)
        self.n_alive_impostors = z3.Int('alive_impostors')
        self.knowns = [] # for known facts that will never change until the game ends

        # State for building facts about players during the game, when what is known
        # might change (I know blue is not murderd and green is not ejected, but then
        # green murders blue, we figure it out and eject green, now blue's murdered
        # state changed and green's ejected state changed)
        self.murdered_pids = []
        self.ejected_pids = []

    def basic_constraints(self):
        """ Returns a list of constraints representing basic facts about the possible game states """
        return [
            # Number of impostors is number of impostors
            self.n_impostors == sumbools(self.impostor)
            # A number of impostors can be alive
            ,self.n_alive_impostors == sumbools(z3.And(self.alive[i], self.impostor[i]) for i in range(self.n_players))
            # People that were murdered cannot be impostors
            ,*[
                z3.Implies(self.murdered[i], z3.Not(self.impostor[i]))
                for i in range(self.n_players)
            ]
            # Alive people have not been murdered and have not been ejected
            ,*[
                z3.And(z3.Not(self.murdered[i]), z3.Not(self.ejected[i])) == self.alive[i]
                for i in range(self.n_players)
            ]
            # There is at least one not-dead impostor
            ,self.n_alive_impostors > z3.IntVal(0)
            # Twice the number of alive impostors is less than the number of alive crewmates
            ,sumbools(self.alive) > (self.n_alive_impostors * z3.IntVal(2))
        ]

    def get_varying_knowns(self):
        """ Builds a list of constraints based on the game state that can change during the game """
        return [
            # People that were murdered were murdered
            *[
                self.murdered[pid] == z3.BoolVal(pid in self.murdered_pids)
                for pid in range(self.n_players)
            ]
            # People that were ejected were ejected
            ,*[
                self.ejected[pid] == z3.BoolVal(pid in self.ejected_pids)
                for pid in range(self.n_players)
            ]
        ]

    def not_this_model(self, model):
        """ Returns a constraint that prevents the given model from being valid """
        return z3.Or(
            *[self.impostor[pid] != model[self.impostor[pid]]
            for pid in range(self.n_players)]
        )

    def combine_solutions(self, models):
        """ Generates the count of models in which each player is an impostor from a
        list of models that satisfy the constraints """
        counts = [0 for _ in range(self.n_players)]
        for model in models:
            for i in range(self.n_players):
                if z3.is_true(model[self.impostor[i]]):
                    counts[i] += 1
        return counts, len(models)

    def check(self):
        """ Find all models, return impostor counts """
        solver = z3.Solver()
        solver.add(
            *self.basic_constraints()
            ,*self.knowns
            ,*self.get_varying_knowns()
        )
        solutions = []
        while True:
            result = solver.check()
            if result == z3.sat:
                solutions.append(solver.model())
                solver.add(self.not_this_model(solver.model()))
            elif result == z3.unsat:
                break
            else:
                raise Exception("Something went wrong: " + result)
        return self.combine_solutions(solutions)

    def set_colours(self, colour_names):
        """ Set the list of names of players (don't actually have to be colours, but it's the
        easiest way to think about it) """
        self.cnames = colour_names

    def pid(self, colour):
        """ Player ID from colour name """
        try:
            return self.cnames.index(colour)
        except ValueError:
            raise WrongColour

    def colour_name(self, pid):
        """ Colour name from Player ID """
        return self.cnames[pid]

    def learn_certain_not_impostor(self, colour):
        """ learn that the player with the specified colour is certainly not an impostor """
        p = self.pid(colour)
        self.knowns.append(
            z3.Not(self.impostor[p])
        )

    def learn_certain_impostor(self, colour):
        """ learn that the player with the specified colour is certainly an impostor """
        p = self.pid(colour)
        self.knowns.append(
            self.impostor[p]
        )

    def learn_murder(self, colour):
        """ Learn that the specified colour has been murdered """
        p = self.pid(colour)
        self.murdered_pids.append(p)

    def learn_ejected(self, colour):
        """ Learn that the specified colour has been ejected"""
        p = self.pid(colour)
        self.ejected_pids.append(p)

    def learn_set_includes_impostors(self, colours):
        """ learn that the players with the specified colours form a group that contains at least one
        player that is certainly an impostor """
        ps = [self.pid(colour) for colour in colours]
        impostor_set = sumbools([self.impostor[p] for p in ps])
        self.knowns.append(
            impostor_set > z3.IntVal(0)
        )



# A quick test case
if __name__ == '__main__':
    num_players = 5
    num_impostors = 1
    game = GameSolver(num_players, num_impostors)
    game.set_colours([
        'red'
        ,'blue'
        ,'green'
        ,'pink'
        ,'orange'
        ,'yellow'
        ,'black'
        ,'white'
        ,'purple'
        ,'brown'
    ])
    # I'm playing as red
    game.learn_certain_not_impostor('red')
    # Pink got murdered
    game.learn_murder('pink') # No need to also learn that they are not an impostor, this is handled for us
    # Blue said they saw green do it, green said they saw blue do it.
    game.learn_set_includes_impostors(['blue', 'green'])
    # We should conclude that there's one way it could be blue, and one way it could be green
    counts, n = game.check()
    if n <= 0:
        print("Uhmmm, something's wrong, sorry.")
    for i in range(num_players):
        if counts[i]:
            print(game.colour_name(i), counts[i])
