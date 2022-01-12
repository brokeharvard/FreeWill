##########################################################################
################################# AMOEBA #################################
##########################################################################

'''
WHAT IS THIS?
    This module is a work in progress. The goal is to create digital amoebas that each have their own genetically
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
'''

import operator
print(dir(operator))
import numpy
import random
import matplotlib
import matplotlib.pyplot as plt
import platform
if platform.system() == 'Darwin':
    matplotlib.use('MacOSX')
else:
    matplotlib.use('TkAgg')

import copy
import traceback
from time import sleep

class World():
    def __init__(self, size=100, initial_being_spawn_count=100, initial_energy_spawn_count=150):
        self.object_world = numpy.zeros(shape=(size,size), dtype=object)
        self.id_world = numpy.zeros(shape=(size,size))
        self.size = size
        self.Emperor_DNA = False    # Longest Being ever to live in this World
        self.Emperor_size = 0
        self.King_DNA = False   # Longest Being that is alive
        self.King_size = 0
        self.Queen_DNA = False  # Second longest Being that is alive
        self.Queen_size = 0
        self.all_Beings = self.spawn_beings(initial_being_spawn_count)
        self.uneaten_Energy = self.spawn_energy(initial_energy_spawn_count)
        self.World_age = 0
        self.all_potential_locations = []

    class Energy(): # Not necessary to have Energy object at this point but adding so have it for later
        def __init__(self, location, energy_count=1):
            self.location = location    # Nested lists with X, Y coordinates; len(Energy.location) always = 1
            self.energy_count = energy_count
            self.energy_id = 2
            # self.energy_id = self.energy_count + 1     #   Can use this if want energy_count to be visible in id_world

    class Being():

        def __init__(self, _World, location, parent_DNA=False):
            self.location = location    # Nested lists with X, Y coordinates
            self.energy = 0
            self.age = 0
            random.seed()
            self.id = random.uniform(1.0, 1.5)  # There is potential for collisions
            if parent_DNA != False:
                random.seed()
                random_index = random.choice(range(len(str(parent_DNA))))
                random_digit = random.choice(list('0123456799'))
                baby_DNA = int((str(parent_DNA)[:random_index] + random_digit + str(parent_DNA)[random_index + 1:]))
                self.DNA = baby_DNA
            else:
                random.seed(self.head_id)
                random_DNA = [random.choice(list('0123456799')) for i in range(250)]
                random_DNA = ''.join(random_DNA)
                random_DNA = int(random_DNA)
                self.DNA = random_DNA
            self.remaining_DNA = self.DNA
            def DNA_slice(remaining_DNA, slice_length):
                slice = int(str(remaining_DNA)[:slice_length])
                self.remaining_DNA = remaining_DNA[slice_length:]
                return slice
            self.reproduction_period = DNA_slice(self.remaining_DNA, 3)
            self.reproduction_number = DNA_slice(self.remaining_DNA, 1)
            self.baby_size = DNA_slice(self.remaining_DNA, 1)


        def update_Being(self, _World):
            self.age = self.age + 1
            self.head  = _World.choose_move(self)
            # self.head = random.choice(potential_locations) # (UPDATE TO ALLOW FOR MORE SOPHISTICATED CHOICE/MUTATIONS LATER)
            if self.head == None:   # This is temporary fix for rare error where Being has no neck for some reason.
                pass
            elif self.energy > 0:
                new_location = [self.head]
                for coordinates in self.location:
                    new_location.append(coordinates)
                self.location = new_location
                self.energy = self.energy - 1
            elif self.energy == 0:
                new_location = [self.head]
                for coordinates in self.location:
                    new_location.append(coordinates)
                del new_location[-1]
                self.location = new_location
            return_package = [self]
            if ((self.age % 100) == 0) and (len(self.location) > 5):
                baby_body = self.location.pop()
                baby_head = self.location.pop()
                baby_location = [baby_head, baby_body]
                print("baby_location = " + str(baby_location))
                baby_Being = _World.Being(_World, baby_location, parent_DNA=self.DNA)
                _World.all_Beings.append(baby_Being)
                counter = 1
                for coordinates in baby_location:   # Think this is unecessary b/c worlds will be recompiled from
                                                    # all_Beings
                    if counter == 1:
                        _World.object_world[coordinates[0], coordinates[1]] = baby_Being
                        _World.id_world[coordinates[0], coordinates[1]] = baby_Being.head_id
                        counter = counter + 1
                    else:
                        _World.object_world[coordinates[0], coordinates[1]] = baby_Being.body_id
                        _World.id_world[coordinates[0], coordinates[1]] = baby_Being.body_id
                return_package.append(baby_Being)

            return return_package

    def update_World(self):
        # Every 100 years, spawn Energy if total_energy is below 298 (World somehow losing energy--this is just a patch
            # until figure out what's going on)
        total_energy = sum([Energy.energy_count for Energy in world.uneaten_Energy] + \
                           [len(Being.location) for Being in world.all_Beings] + \
                           [Being.energy for Being in world.all_Beings])
        # print("Total Energy: " + str(total_energy))
        # print("\tUneaten Energy: " + str(sum([Energy.energy_count for Energy in world.uneaten_Energy])))
        # print("\tSum of Being's Locations: " + str(sum([len(Being.location) for Being in world.all_Beings])))
        # print("\tSum of Being's Unused Energy: " + str(sum([Being.energy for Being in world.all_Beings])))
        if total_energy < 350:
            self.uneaten_Energy = self.uneaten_Energy + self.spawn_energy(350 - total_energy)

        # After specified interval, spawn new Beings if population running low and sufficient uneaten_Energy
        if ((self.World_age % 51) == 0):
            if len(self.all_Beings) < 50:
                total_energy = sum([Energy.energy_count for Energy in world.uneaten_Energy] + \
                                   [len(Being.location) for Being in world.all_Beings] + \
                                   [Being.energy for Being in world.all_Beings])
                if len(self.uneaten_Energy) > 50 - len(self.all_Beings) * 3:
                    spawn_count = 50 - len(self.all_Beings)
                else:
                    spawn_count = int((len(self.uneaten_Energy) - 1) / 2)
                spawned_Beings = self.spawn_beings(spawn_count)
                self.all_Beings = self.all_Beings + spawned_Beings
                for i in range(spawn_count * 2):
                    random.seed()
                    try:
                        del self.uneaten_Energy[
                            random.choice(range(len(self.uneaten_Energy)))]  # Remove Energy to keep equilibrium
                    except:
                        pass

        # Compile updated beings
        updated_beings = []
        copied_all_Beings = copy.deepcopy(self.all_Beings)

        for being in copied_all_Beings:
            # Not sure if have to do below or could just do updated_beings.append(being.update_Being())
            return_package = being.update_Being(self)
            for updated_being in return_package:        # May include baby
                updated_beings.append(updated_being)

        # Create blank updated worlds
        updated_object_world = numpy.zeros(shape=(self.size,self.size), dtype=object)
        updated_id_world = numpy.zeros(shape=(self.size,self.size))

        # Creating lists b/c think faster to iterate through them rather than full world
        updated_being_heads = [updated_being.head for updated_being in updated_beings]
        updated_being_bodies = [updated_being.location[1:] for updated_being in updated_beings]
        uneaten_Energy_locations = [[Energy.location[0][0], Energy.location[0][1]] for Energy in self.uneaten_Energy]

        # Incorporate Energy to updated worlds and uneaten_energy_locations
        for Energy in self.uneaten_Energy:
            updated_object_world[Energy.location[0][0], Energy.location[0][1]] = Energy
            updated_id_world[Energy.location[0][0], Energy.location[0][1]] = Energy.energy_id

        # Incorporate updated_beings to updated worlds
        for updated_being in updated_beings:
            # Shrink one block every 300 years
            if ((updated_being.age % 300) == 0):
                coordinates = updated_being.location.pop(-1) # Delete last block (tail)
                realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]], energy_count=1)
                updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
                self.uneaten_Energy.append(realeased_Energy)

            # If beings' heads collided, both beings die in their updated locations (heads overlapping), with any unused
            # energy of either beings releasing where their heads overlapped
            if updated_being_heads.count(updated_being.head) > 1:
                for coordinates in updated_being.location:
                    if coordinates == updated_being.head:
                        if isinstance(updated_object_world[coordinates[0], coordinates[1]], self.Energy):
                            updated_Energy = updated_object_world[coordinates[0], coordinates[1]]
                            updated_Energy.energy_count = updated_Energy.energy_count + 1 + updated_being.energy
                            updated_object_world[coordinates[0], coordinates[1]] = updated_Energy
                        else:
                            realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]],
                                                           energy_count = 1 + updated_being.energy)
                            updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                            updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
                    else:
                        realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]], energy_count = 1)
                        updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                        updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
            # If being collides with other being's body, being dies without updating location, with any unused
            # releasing at its head
            elif any(updated_being.head in location for location in updated_being_bodies) and \
                    (updated_being.location.count(updated_being.head) == 1):
                for coordinates in updated_being.location:
                    if coordinates == updated_being.head:
                        realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]],
                                                       energy_count=1 + updated_being.energy)
                        updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                        updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
                    else:
                        realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]], energy_count = 1)
                        updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                        updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
            # If being collides with energy, the being consumes the energy and saves it for growing in subsequent
            # round(s)
            elif updated_being.head in uneaten_Energy_locations:
                updated_being.energy = updated_being.energy + \
                                       updated_object_world[updated_being.head[0], updated_being.head[1]].energy_count
                for coordinates in updated_being.location:
                    if coordinates == updated_being.head:
                        updated_object_world[coordinates[0], coordinates[1]] = updated_being
                        updated_id_world[coordinates[0], coordinates[1]] = updated_being.head_id
                    else:
                        updated_object_world[coordinates[0], coordinates[1]] = updated_being.body_id
                        updated_id_world[coordinates[0], coordinates[1]] = updated_being.body_id
                uneaten_Energy_locations.remove(updated_being.head)
            # If being too small for age, kill being
            elif ((updated_being.age % 50) == 0) and len(updated_being.location) < (2 + (updated_being.age/50)):
                for coordinates in updated_being.location:
                    if coordinates == updated_being.head:
                        realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]],
                                                       energy_count=1 + updated_being.energy)
                        updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                        updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
                    else:
                        realeased_Energy = self.Energy([[coordinates[0], coordinates[1]]], energy_count = 1)
                        updated_object_world[coordinates[0], coordinates[1]] = realeased_Energy
                        updated_id_world[coordinates[0], coordinates[1]] = realeased_Energy.energy_id
                pass
            # If being collides with nothing, it's location is updated unless it is told, in which case it dies
            else:
                for coordinates in updated_being.location:
                    if coordinates == updated_being.head:
                        updated_object_world[coordinates[0], coordinates[1]] = updated_being
                        updated_id_world[coordinates[0], coordinates[1]] = updated_being.head_id
                    else:
                        updated_object_world[coordinates[0], coordinates[1]] = updated_being.body_id
                        updated_id_world[coordinates[0], coordinates[1]] = updated_being.body_id

        # Update world
        self.object_world = updated_object_world
        self.id_world = updated_id_world
        updated_all_Beings = []
        updated_uneaten_Energy = []
        for coordinates, obj in numpy.ndenumerate(self.object_world):     # Iterate through current object_world
            if isinstance(obj, self.Being):
                updated_all_Beings.append(obj)
            if isinstance(obj, self.Energy):
                updated_uneaten_Energy.append(obj)
        self.all_Beings = updated_all_Beings
        self.uneaten_Energy = updated_uneaten_Energy
        for Being in self.all_Beings:
            if len(Being.location) > self.Emperor_size:
                self.Emperor_DNA = Being.DNA
                self.Emperor_size = len(Being.location)
            if len(Being.location) > self.King_size:
                self.Queen_DNA = self.King_DNA
                self.Queen_size = self.King_size
                self.King_DNA = Being.DNA
                self.King_size = len(Being.location)
            elif len(Being.location) > self.Queen_size:
                self.Queen_DNA = Being.DNA
                self.Queen_size = len(Being.location)
        self.World_age = self.World_age + 1


    def choose_math_operation(self, DNA_strand):
        ops = [
            # Returning number
            operator.add,
            operator.sub,
            operator.mul,
            operator.truediv,
            operator.floordiv,
            # operator.pow,     # This resulted in TypeError: can't convert complex to float
            operator.mod,
            # Returning boolean (can convert to number)
            # operator.lt,
            # operator.le,
            # operator.eq,
            # operator.gt,
            # operator.ge,
            # operator.ne,
        ]
        random.seed(DNA_strand)
        operation = random.choice(ops)
        return operation

    def processing_single_cell(_World, Being, cell, potential_locations, DNA):
        processing_results = []
        try:
            cell_id = _World.id_world[cell[0], cell[1]]
        except: # Cell isn't part of World grid
            cell_id = 0
        processing_results.append(cell_id)
        is_option = int(bool(str(cell_id) in str(potential_locations)))
        processing_results.append(is_option)
        diff_x = cell[0] - Being.head[0]
        processing_results.append(diff_x)
        diff_y = cell[1] - Being.head[0]
        processing_results.append(diff_y)
        '''
        for i in range(3):
            DNA = int(str(DNA)[2:])
            random.seed(int(str(DNA)[0:8]))
            # number_of_operations = random.choice([1, 2])
            # for i in range (number_of_operations):        # Implement this later
            DNA = int(str(DNA)[2:])
            random.seed(int(str(DNA)[0:8]))
            n = random.uniform(-1,1)
            DNA = int(str(DNA)[2:])
            random.seed(int(str(DNA)[0:8]))
            operation = _World.choose_math_operation(DNA)
            calc_result = operation(cell_id, n)
            processing_results.append(calc_result)
        '''
        return [processing_results, DNA]

    def choose_move(_World, Being):

        try:

            def near_vision(_World, x, y): # Currently not used
                near_coords = [
                    [x-2, y+2], [x-1, y+2], [x, y+2], [x+1, y+2], [x+2, y+2],
                    [x-2, y+1], [x-1, y+1], [x, y+1], [x+1, y+1], [x+2, y+1],
                    [x-2,   y], [x-1,   y], [x,   y], [x+1,   y], [x+2,   y],
                    [x-2, y-1], [x-1, y-1], [x, y-1], [x+1, y-1], [x+2, y-1],
                    [x-2, y-2], [x-1, y-2], [x, y-2], [x+1, y-2], [x+2, y-2],
                ]
                near_ids = []
                for coord in near_coords:
                    id = _World.id_world[coord[0], coord[1]]
                    near_ids.append(id)
                return near_ids

            def straight_vision(_World, x, y):

                def north_distance_to_object(_World, x, y, distance=1):
                    try:
                        forward_block = _World.id_world[x, y+1]
                        if forward_block == 0.0:        # Empty block
                            distance = distance + 1
                            y = y+1
                            return north_distance_to_object(_World, x, y, distance=distance)
                        else:
                            if forward_block == 2:
                                energy = True
                            else:
                                energy = False
                            return [distance, energy]
                    except:     # forward_block is off the World grid
                        energy = False
                        return [distance, energy]

                def south_distance_to_object(_World, x, y, distance=1):
                    try:
                        forward_block = _World.id_world[x, y-1]
                        if forward_block == 0.0:        # Empty block
                            distance = distance + 1
                            y = y-1
                            return south_distance_to_object(_World, x, y, distance=distance)
                        else:
                            if forward_block == 2:
                                energy = True
                            else:
                                energy = False
                            return [distance, energy]
                    except:  # forward_block is off the World grid
                        energy = False
                        return [distance, energy]

                def east_distance_to_object(_World, x, y, distance=1):
                    try:
                        forward_block = _World.id_world[x + 1, y]
                        if forward_block == 0.0:  # Empty block
                            distance = distance + 1
                            x = x + 1
                            return east_distance_to_object(_World, x, y, distance=distance)
                        else:
                            if forward_block == 2:
                                energy = True
                            else:
                                energy = False
                            return [distance, energy]
                    except:  # forward_block is off the World grid
                        energy = False
                        return [distance, energy]

                def west_distance_to_object(_World, x, y, distance=1):
                    try:
                        forward_block = _World.id_world[x-1, y]
                        if forward_block == 0.0:        # Empty block
                            distance = distance + 1
                            x = x-1
                            return west_distance_to_object(_World, x, y, distance=distance)
                        else:
                            if forward_block == 2:
                                energy = True
                            else:
                                energy = False
                            return [distance, energy]
                    except:  # forward_block is off the World grid
                        energy = False
                        return [distance, energy]

                return_package = north_distance_to_object(_World, x, y)
                north_distance = return_package[0]
                north_energy = return_package[1]
                return_package = south_distance_to_object(_World, x, y)
                south_distance = return_package[0]
                south_energy = return_package[1]
                return_package = east_distance_to_object(_World, x, y)
                east_distance = return_package[0]
                east_energy = return_package[1]
                return_package = west_distance_to_object(_World, x, y)
                west_distance = return_package[0]
                west_energy = return_package[1]

                output_package = [north_distance, north_energy, south_distance, south_energy, east_distance,
                                  east_energy, west_distance, west_energy]
                return output_package

            def smell(_World, x, y):
                near_coords = [
                    [x-1, y+1], [x, y+1], [x+1, y+1],
                    [x-1,   y], [x,   y], [x+1,   y],
                    [x-1, y-1], [x, y-1], [x+1, y-1],
                ]
                uneaten_Energy = _World.uneaten_Energy
                closest_Energy_location = False
                for Energy in uneaten_Energy:
                    EnergyX = Energy.location[0][0]
                    EnergyY = Energy.location[0][1]
                    distance = abs(x-EnergyX) + abs(y-EnergyY)
                    if closest_Energy_location == False:
                        closest_Energy_location = Energy.location[0]
                        closest_distance = distance
                    elif closest_distance > distance:
                        closest_Energy_location = Energy.location[0]
                        closest_distance = distance
                try:
                    CEL_X = closest_Energy_location[0]
                    CEL_Y = closest_Energy_location[1]
                    closest_potential_location = False
                    for option in near_coords:
                        optionX = option[0]
                        optionY = option[1]
                        distance = abs(CEL_X-optionX) + abs(CEL_Y-optionY)
                        if closest_potential_location == False:
                            closest_potential_location = option
                            closest_distance = distance
                        elif closest_distance > distance:
                            closest_potential_location = option
                            closest_distance = distance
                except:
                    closest_potential_location = None
                    closest_distance = 0
                return_package = [closest_potential_location, closest_distance]
                return return_package

            data_list = []
            for data in near_vision(_World, x, y):
                data_list.append(data)
            for data in straight_vision(_World, x, y):
                data_list.append(data)
            for data in smell(_World, x, y):
                data_list.append(data)

            #YOU ARE HERE!!!

            pre_processing_results = []

            ### OLD WAY:
            # for cell in near_vision:
            #     output = _World.processing_single_cell(Being, cell, potential_locations, DNA)
            #     results = output[0]
            #     DNA = output[1]
            #     for result in results:
            #         DNA = int(str(DNA)[2:])
            #         random.seed(int(str(DNA)[0:8]))
            #         processing_results.append(result * random.uniform(-1,1))

            ### NEW WAY (STILL NOT SOPHISTICATED):
            for data in data_list:
                ### Pre-Process Option 1
                pre_processing_results.append(data)
                ### Pre-Process Option 2
                # DNA = int(str(DNA)[2:])
                # random.seed(int(str(DNA)[0:8]))
                # number_of_operations = random.choice([1, 2])
                # input = sight_result
                # for i in range (number_of_operations):        # Implement this later
                #     DNA = int(str(DNA)[2:])
                #     random.seed(int(str(DNA)[0:8]))
                #     n = random.uniform(-1,1)
                #     DNA = int(str(DNA)[2:])
                #     random.seed(int(str(DNA)[0:8]))
                #     operation = _World.choose_math_operation(DNA)
                #     input = operation(input, n)
                # pre_processing_results.append(input)
                pass

            ### Pre-Process Option 3
            # for i in range(5):
            #     intake_neuron = []
            #     for sight_result in sight_results:
            #         input = sight_result
            #         DNA = int(str(DNA)[2:])
            #         random.seed(int(str(DNA)[0:8]))
            #         n = random.uniform(-1, 1)
            #         intake_neuron.append(n * input)
            #     intake_result = sum(intake_neuron)
            #     pre_processing_results.append(intake_result)


            processing_results = []
            for pre_processing_result in pre_processing_results:
                ### Option 1
                processing_results.append(pre_processing_result)

                ### Option 2
                # DNA = int(str(DNA)[2:])
                # random.seed(int(str(DNA)[0:8]))
                # number_of_operations = random.choice([1, 2])
                # input = pre_processing_result
                # for i in range (number_of_operations):
                #     DNA = int(str(DNA)[2:])
                #     random.seed(int(str(DNA)[0:8]))
                #     n = random.uniform(-1,1)
                #     DNA = int(str(DNA)[2:])
                #     random.seed(int(str(DNA)[0:8]))
                #     operation = _World.choose_math_operation(DNA)
                #     input = operation(input, n)
                # processing_results.append(input)
            # for i in range(3):
            #     DNA = int(str(DNA)[2:])
            #     random.seed(int(str(DNA)[0:8]))
            #     input1 = random.choice(pre_processing_results)
            #     DNA = int(str(DNA)[2:])
            #     random.seed(int(str(DNA)[0:8]))
            #     number_of_operations = random.choice([1, 2])
            #     for i in range (number_of_operations):
            #         DNA = int(str(DNA)[2:])
            #         random.seed(int(str(DNA)[0:8]))
            #         input2 = random.choice(pre_processing_results)
            #         DNA = int(str(DNA)[2:])
            #         random.seed(int(str(DNA)[0:8]))
            #         operation = _World.choose_math_operation(DNA)
            #         try:
            #             input1 = operation(input1, input2)
            #         except:
            #             input1 = 0
            #     processing_results.append(input1)

            ### YOU ARE HERE!!

            first_loop = True
            for potential_location in potential_locations:
                DNA = Being.DNA
                assessment_value = 0
                for result in processing_results:
                    DNA = int(str(DNA)[2:])
                    random.seed(int(str(DNA)[0:8]))
                    assessment_value = assessment_value + (result * random.uniform(-1,1))
                DNA = int(str(DNA)[2:])
                random.seed(int(str(DNA)[0:8]))
                potential_location_conflict_number = (all_potential_locations.count(potential_location) - 1)
                # assessment_value = assessment_value + (potential_location_conflict_number * random.uniform(-100, 100))
                assessment_value = assessment_value + (potential_location_conflict_number * 100)  # FOR DEBUGGING PURPOSES
                if potential_location == potential_location_closest_to_Energy:
                    ### Option 1
                    # DNA = int(str(DNA)[2:])
                    # random.seed(int(str(DNA)[0:8]))
                    # number_of_operations = random.choice([1, 2])
                    # variable = distance_to_closest_Energy
                    # for i in range(number_of_operations):  # Implement this later
                    #     DNA = int(str(DNA)[2:])
                    #     random.seed(int(str(DNA)[0:8]))
                    #     n = random.uniform(-10, 10)
                    #     DNA = int(str(DNA)[2:])
                    #     random.seed(int(str(DNA)[0:8]))
                    #     operation = _World.choose_math_operation(DNA)
                    #     variable = operation(variable, n)
                    # random.seed(int(str(DNA)[0:8]))
                    # DNA = int(str(DNA)[2:])
                    # assessment_value = assessment_value + (variable * random.uniform(-1,1))
                    ### Option 2
                    DNA = int(str(DNA)[2:])
                    random.seed(int(str(DNA)[0:8]))
                    n = random.uniform(-10, 10)
                    assessment_value = assessment_value + (n * random.uniform(-1,1))
                if potential_location in die_locations:
                    ### Option 1
                    # DNA = int(str(DNA)[2:])
                    # random.seed(int(str(DNA)[0:8]))
                    # number_of_operations = random.choice([1, 2])
                    # variable = 1
                    # for i in range(number_of_operations):  # Implement this later
                    #     DNA = int(str(DNA)[2:])
                    #     random.seed(int(str(DNA)[0:8]))
                    #     n = random.uniform(-10, 10)
                    #     DNA = int(str(DNA)[2:])
                    #     random.seed(int(str(DNA)[0:8]))
                    #     operation = _World.choose_math_operation(DNA)
                    #     variable = operation(variable, n)
                    # assessment_value = assessment_value + (variable * random.uniform(-10,10))
                    ### Option 2
                    DNA = int(str(DNA)[2:])
                    random.seed(int(str(DNA)[0:8]))
                    # assessment_value = assessment_value - (assessment_value * random.uniform(-100,100))
                    assessment_value = assessment_value + abs(assessment_value * 100)  # FOR DEBUGGING PURPOSES
                if first_loop == True:
                    if (potential_location[0] <= 99) and (potential_location[0] >= 0) and (potential_location[1] <= 99) and \
                            (potential_location[1] >= 0):    # Off the grid
                        chosen_move = potential_location
                        first_loop = False
                        best = assessment_value
                else:
                    if float(assessment_value) < float(best):
                        if (potential_location[0] <= 99) and (potential_location[0] >= 0) and (potential_location[1] <= 99) and \
                                (potential_location[1] >= 0):  # Off the grid
                            chosen_move = potential_location
            return chosen_move

        except Exception as e:
            print("Uh oh... Ran into error while choosing move: " + str(e))
            traceback.print_exc()
            return None

    def compile_random_spawn_locations(self, spawn_count, spawning_beings=True):

        def add_random_location(spawn_locations, spawning_beings=True, taken_locations=[]):
            if spawning_beings == True:
                random.seed()
                random_head_location = [random.choice(range(99)), random.choice(range(99))]
                if random_head_location not in taken_locations:
                    x = random_head_location[0]
                    y = random_head_location[1]
                    potential_neck_locations = [[x, y + 1], [x - 1, y], [x + 1, y], [x, y - 1]]
                    random_neck_location = spawn_random_neck_location(random_head_location, potential_neck_locations,
                                                                      spawn_locations, taken_locations=taken_locations)
                    if random_neck_location != False:
                        random_location = [random_head_location, random_neck_location]
                        spawn_locations.append(random_location)
                        taken_locations.append(random_head_location)
                        taken_locations.append(random_neck_location)
                        return [spawn_locations, taken_locations]
                    else:
                        return add_random_location(spawn_locations, spawning_beings=spawning_beings,
                                                   taken_locations=taken_locations)
                else:
                    return add_random_location(spawn_locations, spawning_beings=spawning_beings,
                                               taken_locations=taken_locations)
            elif spawning_beings == False:
                random_location = [[random.choice(range(99)), random.choice(range(99))]]
                if random_location not in taken_locations:
                    spawn_locations.append(random_location)
                    taken_locations.append(random_location)
                    return [spawn_locations, taken_locations]
                else:
                    return add_random_location(spawn_locations, spawning_beings=spawning_beings,
                                               taken_locations=taken_locations)

        def spawn_random_neck_location(head_location, potential_neck_locations, spawn_locations, taken_locations=[]):
            random_neck_location = random.choice(potential_neck_locations)
            if random_neck_location not in taken_locations:
                return random_neck_location
            else:
                potential_neck_locations.remove(random_neck_location)
                if not potential_neck_locations:
                    return False
                elif potential_neck_locations:
                    return spawn_random_neck_location(head_location, potential_neck_locations, spawn_locations,
                                                      taken_locations=taken_locations)

        spawn_locations = []
        taken_locations = []
        for coordinates, id in numpy.ndenumerate(self.id_world):
            if id != 0:
                taken_locations.append(coordinates)
        for i in range(spawn_count):
            output = add_random_location(spawn_locations, spawning_beings=spawning_beings,
                                         taken_locations=taken_locations)
            spawn_locations = output[0]
            taken_locations = output[1]
        return spawn_locations

    def spawn_beings(self, spawn_count):
        locations = self.compile_random_spawn_locations(spawn_count, spawning_beings=True)
        Beings = []
        for location in locations:
            spawned_Being = self.Being(self, location)
            counter = 1
            for coordinates in location:
                if counter == 1:
                    self.object_world[coordinates[0], coordinates[1]] = spawned_Being
                    self.id_world[coordinates[0], coordinates[1]] = spawned_Being.head_id
                    counter = counter + 1
                else:
                    self.object_world[coordinates[0], coordinates[1]] = spawned_Being.body_id
                    self.id_world[coordinates[0], coordinates[1]] = spawned_Being.body_id
            Beings.append(spawned_Being)
        return(Beings)

    def spawn_energy(self, spawn_count, energy_count=1):
        locations = self.compile_random_spawn_locations(spawn_count, spawning_beings=False)
        uneaten_Energy = []
        for location in locations:
            spawned_Energy = self.Energy(location, energy_count=energy_count)
            for coordinates in location:
                self.object_world[coordinates[0], coordinates[1]] = spawned_Energy
                self.id_world[coordinates[0], coordinates[1]] = spawned_Energy.energy_id
            uneaten_Energy.append(spawned_Energy)
        return(uneaten_Energy)

    # class universal_laws():
    #     def __init__(self, location):

    # class chromosomes():
    #     def __init__(self, location):



def operate(a, b, operation):
    try:
        operation(a, b)
    except:
        try:
            operation(a)
        except:
            False

if __name__ == "__main__":
    # def main_run():
    world = World()
    plt.imshow(world.id_world)
    plt.clim(0, 30) # colorbar will be based on min value of 0 and max value of 30
    plt.colorbar()
    plt.pause(0.01)
    while True:
    # for i in range(3):
    #     if len(world.all_Beings) < 25:
    #         print("Spawning 25 new Beings")
    #         world.all_Beings = world.all_Beings + world.spawn_beings(25)
        world.update_World()
        plt.clf()
        total_energy = sum([Energy.energy_count for Energy in world.uneaten_Energy] + \
                           [len(Being.location) for Being in world.all_Beings] + \
                           [Being.energy for Being in world.all_Beings])
        plt.title("World Age: " + str(world.World_age) + "\nTotal Energy: " + str(total_energy) + \
                  "\nEmperor Size: " + str(world.Emperor_size) + "\n King "
                  "Size: " + str(world.King_size))
        plt.imshow(world.id_world)
        plt.colorbar()
        plt.pause(0.01)
        print("Loop " + str(world.World_age) + " complete. Emperor Length = " + str(world.Emperor_size) + \
              " Emperor_DNA = " + str(world.Emperor_DNA) + " + King_DNA = " + str(world.King_DNA) + \
              "  Queen_DNA = " + str(world.Queen_DNA))


    # import cProfile
    # pr = cProfile.Profile()
    # pr.enable()
    # main_run()
    # pr.disable()
    # pr.print_stats(sort='time')


