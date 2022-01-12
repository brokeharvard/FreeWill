# FreeWill
The goal of this repository is to create artificially intelligent digital organisms. It is a work in progress. Feel 
free to contribute! Existing and planned modules are as follows:



    SLITHER:  Digital snakes that each have their own genetically evolved artificial intelligence. The snakes live in a
    virtual 2D world with confined resources/energy. Consuming energy increases the length of the snake at a
    one-to-one ratio through an extension of the length of snake (from its tail) in the next iteration of the world.
    The snakes must move head first in each iteration of the world. They can curl up/overlap on themselves,
    but if they move into a space occupied by another snake, they will die, and their body will be converted into
    energy at a one-to-one ratio. The rules of the world are inspired by slither.io.

    AMOEBA:  This module is a work in progress. The goal is to create digital amoebas that each have their own genetically
    evolved artificial intelligence. The amoebas will live in a virtual 2D world with confined resources/energy.
    Consuming energy will increase the size of the amoebas at a one-to-one ratio. If an amoeba dies, its body will be
    converted into energy at a one-to-one ratio. Unlike the snakes of the Slither module, the amoebas will be able to
    choose:
        - where to increase in size (rather than always growing from their tail)
        - when to move (they need not move in each iteration of the world, though they will likley be required to
          move a defined minimum amount to avoid a static world; alternatively, could provide a mechanism for
          non-static amoebas to kill static amoebas)
        - where to move from (they need not move from their tail)
    Given the greater freedom of choice of the amoebas (when compared to the snakes of the Slither module),
    this module is expected to be significantly more demanding to process. Hardware constraints may ultimately be a
    limiting factor.

    ATOM:  This is a placeholder for a planned module that will create digital "atoms" that each have their own
    genetically evolved artificial intelligence/genetic rule set for interacting with their virtual 2D world. Each
    atom will occupy only a single space in the virtual world. The goal is to explore whether this framework can be
    used to evolve more complex organisms that are composed of multiple atoms. Draws inspiration from Conway's Game of
    Life, but differs in that, rather than all spaces in the 2D world abiding by the same rule set:
        - each atom will have its own AI/genetic rule set
        - the virtual 2D world will have empty spaces