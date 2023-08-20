# A User class
# One of its attributes 

#     A single class to represent collections

#         User attributes

#             user id,

#             population type,

#             embedded collection (or document?) division info dictionary of dictionaries

#                 "division_info" : [
#                     {
#                         "division_id":,
#                         "division_name": ,
#                         "reward_one":,
#                         "reward_zero":,
#                         "rewards_so_far":,
#                         "times_selected":,
#                         "products2selectionCount": {}
#                     },
#                     {

#                     }
#                 ]

#         In future if I want to add more collections like Products, Divisions, Populations, they will all be associated with User collection through IDs in each document 




class user_data:

    def __init__(self):
        self.user_id = None
        self.population_type = None


        # {
        #         "division_id": division_id,
        #         "division_name": division_name,
        #         "reward_one": 0,
        #         "reward_zero": 0,
        #         "products2selectionCount": {}
        # }

        self.division_info_thompson = list() 

        # {
        #         "division_id": division_id,
        #         "division_name": division_name,
        #         "rewards_so_far": 0,
        #         "times_selected": 0,
        #         "products2selectionCount": {}
        # }

        self.division_info_ucb = list() 

        self.division_info_random = list()


        self.total_clicks_thompson = 0
        self.total_clicks_ucb = 0
        self.total_clicks_random = 0


    def add_division_info_thompson( self,  division_name  ):
        info_dict_thompson = {

                "division_name": division_name,
                "reward_one": 0,
                "reward_zero": 0,
                "products2selectionCount": {}
        }


        self.division_info_thompson.append( info_dict_thompson )



    def add_division_info_ucb(self, division_name ):
        info_dict_ucb = {

                "division_name": division_name,
                "rewards_so_far": 0,
                "times_selected": 0,
                "products2selectionCount": {}
        }


        self.division_info_ucb.append( info_dict_ucb)


    def add_division_info_random(self,  division_name):
        info_dict_random = {
                "division_name": division_name,
                "rewards_so_far": 0,
                "products2selectionCount": {}

        }
        self.division_info_random.append( info_dict_random )



    def update_division_info_thompson(self, division_name, reward_type):

        if reward_type=="reward_one":
            self.total_clicks_thompson += 1

        for info_dict in self.division_info_thompson:
            if (info_dict["division_name"]==division_name):
                info_dict[reward_type] += 1


    def update_division_info_ucb(self, division_name, reward):

        for info_dict in self.division_info_ucb:
            if info_dict["division_name"]==division_name:
                info_dict["times_selected"] += 1
                if reward==1:
                    info_dict["rewards_so_far"] += 1
                    self.total_clicks_ucb += 1



    def update_division_info_random(self, division_name, reward):

        for info_dict in self.division_info_random:
            if info_dict["division_name"]==division_name:
                info_dict["rewards_so_far"] += reward

                # print(info_dict["rewards_so_far"])

                if reward==1:
                    self.total_clicks_random += 1


    def get_division_info_thompson( self  ):

        # for info_dict in self.division_info_thompson:
        #   if info_dict["division_name"] = division_name:
        #       return info_dict

        return self.division_info_thompson

    def get_division_info_ucb( self ):

        # for info_dict in self.division_info_thompson:
        #   if info_dict["division_name"] = division_name:
        #       return info_dict

        return self.division_info_ucb



    def get_division_info_random( self  ):

        # for info_dict in self.division_info_random:
        #   if info_dict["division_name"] = division_name:
        #       return info_dict

        return self.division_info_random


    def set_user_id(self, user_id):
        self.user_id = user_id


    def set_population_type(self, population_type ):
        self.population_type = population_type



    def get_user_id(self):
        return self.user_id

    def get_population_type(self):
        return self.population_type



    def total_clicks_thompson(self):
        return self.total_clicks_thompson


    def total_clicks_ucb(self):
        return self.total_clicks_ucb


    def total_clicks_random(self):
        return self.total_clicks_random



    def display_user_data(self):

        print( self.user_id )
        print( self.division_info_thompson) 
        print( self.division_info_random)
        print( self.division_info_ucb)


















