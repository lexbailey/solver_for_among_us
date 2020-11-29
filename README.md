# Solver for Among Us

Tell it what you know, it remembers for you, calculates all the possible explanations for the information you've given it, tells you who to vote for.

You can tell it when:
 - a person is murdered
 - a person is ejected
 - you find out that a person is an impostor (eject confirmed, seen kill, seen vent)
 - you find out that a person is not an impostor (visual task seen)
 - you know for sure that a particular group of people contains at least one impostor (for example you [red] saw green and black for the whole round, but there's been a kill. All other players except red, green, and black, must include at least one impostor.)

That last point in the list is the important one.

## Video

There's a video explanation of this on youtube here:

https://youtu.be/G-ojENewj6o

## Screenshot

![Screenshot of solver GUI](https://github.com/danieljabailey/solver_for_among_us/raw/master/screenshots/screenshot2.png)

## Platforms

Tested on Ubuntu, probably works on must linux distros.
Only depends on python3 and some python3 modules, so can easily be ported to any system that can run these.

## Installation

    ./initvenv

## Running

    ./run

## Usage

Navigate to `localhost:5000` in your browser.
When you are in the Among Us lobby, tick all of the colours of the players, then select the number of impostors in the game, click "Start game"

During the game, provide information as follows:
 - Person is murdered: click "Murdered" on the murdered colour
 - Person is ejected: click "Ejected" on the ejected colour, then if confirm-ejects is on, also click "Crewmate" or "Impostor" accordingly on the same colour
 - Person is seen to be a crewmate: click "Crewmate" on the seen colour
 - Person is seen to be an impostor: click "Impostor" on the seen colour
 - A group of people is found to contain at least one impostor: click the [red] cross symbols on all colours in that group, to change them to [green] tick symbols, then click "Selection contains at least one impostor"

When voting starts, look at the list of people to vote for under "Who to eject?". The topmost entry in the list is the most likely to be an impostor.

Note: several people may be equally likely to be impostors, given the known information. Ties are broken in the order of colours on screen, left to right top to bottom.

## How it works

This solver uses z3 to find every model that explains the known information. It finds the total number of models in which each player is an impostor, this is reported on the GUI as the "Models" number.

The number of models that a player is in is a heuristic for the probability that they are an impostor.

The rules of the game are encoded in a form that z3 understands. The logic to figure out who the impostors are is never described anywhere. z3 figures this out for itself.

## FAQ

Q: Is this an AI?

A: No. It hasn't learned the game from the rules, it just has knows how to check if a game state is valid given the rules, and it finds all valid states (models).


Q: Why did you make this?

A: For fun.


Q: Does this help you cheat at Among Us?

A: No. I tried using it to play Among Us. It doesn't help. It's hopelessly impractical.


Q: Why does the ui look so bad?

A: Yes.


Q: I found a problem, how do I report it?

A: Raise an issue using the issues tab above.

