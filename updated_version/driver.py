import json
import os
import time


# Importing the general data manipulation libraries
import pandas as pd
import numpy as np
import random
from random import choices


from data_model import user_data
from utils import recommendation_by_thompson, recommendation_by_ucb, recommendation_by_random, get_division_probabilities, chi_squared_test_for_independence, t_test_for_difference_of_means


# Read the dataset
DF_ITEMS = pd.read_csv('Items_without_duplicates.csv')
DF = DF_ITEMS[ ['dept_name', 'prod_name'] ]



start_time = time.time()

TOTAL_TRIALS_PER_USER = 200
TOTAL_USERS_PER_POPULATION = 2000
TOTAL_TRIALS_PER_POPULATION = TOTAL_USERS_PER_POPULATION * TOTAL_TRIALS_PER_USER



DIVISION_2_ITEMS = {}
for group, frame in DF.groupby('dept_name'):
    # print(group)
    DIVISION_2_ITEMS[str(group)] = list( frame['prod_name'] )

DIVISIONS = list()
for division in DIVISION_2_ITEMS.keys():
    DIVISIONS.append(division)


USER_BIAS_TOWARD_DIVISIONS = get_division_probabilities(DIVISIONS)



# Process_0

#     Y = Process_0( X )

#     X:

#         Empty user collection (an empty list of user objects),
#         Total users,
#         list of algorithms (or population types),
#         list of product divisions/categories,

#     Process_0:

#         Add documents to those collections

#         Basically, create a list of User objects with the attributes initialized to their respective initial values 


#     Y:
#         The list of user objects
def initialize_user_collection( total_users_per_population, list_of_population_types, list_of_divisions  ):

    global DIVISIONS
    list_of_population_types = ["random", "thompson", "ucb"]
    collection_of_users = list()
    user_idx = 1
    for population_type in list_of_population_types:
        for user_id in range( user_idx, user_idx + total_users_per_population):

            # create an instance of user_data
            user_document = user_data()

            # set user id and population_type

            user_document.set_user_id( user_id )
            user_document.set_population_type( population_type )

            for division_id in range( 1, len(DIVISIONS)+1 ):

                user_document.add_division_info_thompson(  DIVISIONS[division_id-1] )
                user_document.add_division_info_ucb(  DIVISIONS[division_id-1] )
                user_document.add_division_info_random(  DIVISIONS[division_id-1] )

            collection_of_users.append( user_document )

            # user_document.display_user_data()
        # print( "  " )

        user_idx = user_id + 1

    return collection_of_users



# Process_1

#     Y = Process_1( X )


#     X:
#         list of users, 
#         Algorithm type, 
#         total trials per user, 
#         Product Category Selection Bias


#     Process_1:

#         Run trials for each algorithm (or population type)

#         For every user
            
#             For n'th trial of total trials

#                 Get the user's population type,
#                 Based on algorithm/population type and relevant user attributes get a certain product recommended,

#                 Based on product category selection bias, accept or reject recommendation,

#                 Based on choice, update current user's embedded division collection info


#     Y:
#         Interaction data for each algorithm OR basically all data captured in each user object (OR document)

def generate_interaction_data_from_multiple_runs( collection_of_users, algorithm_type, total_trials_per_user, user_bias_toward_divisions ):

    list_of_population_types = ["random", "thompson", "ucb"]

    # temp_list_of_users = list()

    for user_document in collection_of_users:



        if algorithm_type == "thompson":

            if user_document.get_population_type() != "thompson":
                continue

            trials_so_far = 0
            while trials_so_far <= total_trials_per_user:

                division_info_thompson = user_document.get_division_info_thompson()

                recommended_division, user_decision = recommendation_by_thompson( trials_so_far, user_bias_toward_divisions, DIVISIONS, division_info_thompson )


                # Update the user_document based on decisions
                reward_type = ""
                if user_decision==1:
                    reward_type = "reward_one"
                else:
                    reward_type = "reward_zero"

                user_document.update_division_info_thompson( recommended_division, reward_type )

                # print(reward_type, recommended_division)
                trials_so_far += 1


        elif algorithm_type == "ucb":

            if user_document.get_population_type() != "ucb":
                continue


            trials_so_far = 0
            while trials_so_far <= total_trials_per_user:


                division_info_ucb = user_document.get_division_info_ucb()

                recommended_division, user_decision = recommendation_by_ucb( trials_so_far, user_bias_toward_divisions, DIVISIONS, division_info_ucb )

                reward = 0
                if user_decision == 1:
                    reward = 1

                user_document.update_division_info_ucb( recommended_division, reward )
                trials_so_far += 1
                                                            


        elif algorithm_type == "random":

            if user_document.get_population_type() != "random":
                continue

            trials_so_far = 0
            while trials_so_far <= total_trials_per_user:


                division_info_random = user_document.get_division_info_random()

                recommended_division, user_decision = recommendation_by_random( user_bias_toward_divisions, DIVISIONS, division_info_random )

                reward = 0
                if user_decision == 1:
                    reward = 1
                    # print("selection happened", recommended_division, user_document.user_id)
                    # temp_list_of_users.append(user_document.user_id)

                user_document.update_division_info_random( recommended_division, reward )
                trials_so_far += 1





def check_if_algorithm_type_affects_user_decisions( collection_of_users, total_trials_per_population, list_of_population_types ):
    

    population_type_2_total_clicks = dict()
    population_type_2_total_clicks["thompson"] = 0
    population_type_2_total_clicks["ucb"] = 0
    population_type_2_total_clicks["random"] = 0

    for user_document in collection_of_users:
        if user_document.get_population_type() == "thompson":
            population_type_2_total_clicks["thompson"] += user_document.total_clicks_thompson
    
        elif user_document.get_population_type() == "ucb":
            population_type_2_total_clicks["ucb"] += user_document.total_clicks_ucb
    
        elif user_document.get_population_type() == "random":
            population_type_2_total_clicks["random"] += user_document.total_clicks_random


    print(population_type_2_total_clicks)
    bool_algo_type_affects_user_decisions = chi_squared_test_for_independence( population_type_2_total_clicks, total_trials_per_population)

    return bool_algo_type_affects_user_decisions



def check_for_significant_difference_between_clicks_due_to_algo_type( collection_of_users ):

    mu_thompson = None
    mu_ucb = None
    # total_clicks_thompson = 0
    # total_clicks_ucb = 0
    list_of_thompson_user_clicks = list()
    list_of_ucb_user_clicks = list()
    for user_document in collection_of_users:

        if user_document.get_population_type() == "thompson":

            list_of_thompson_user_clicks.append( user_document.total_clicks_thompson )

        elif user_document.get_population_type() == "ucb":

            list_of_ucb_user_clicks.append( user_document.total_clicks_ucb )
        
    mu_thompson = np.mean( np.array( list_of_thompson_user_clicks ) )
    mu_ucb = np.mean( np.array( list_of_ucb_user_clicks ) )

    s_thompson = np.std( np.array( list_of_thompson_user_clicks ) )
    s_ucb = np.std( np.array( list_of_ucb_user_clicks ) )

    total_data_pts_thompson = len( list_of_thompson_user_clicks )
    total_data_pts_ucb = len( list_of_ucb_user_clicks )

    bool_difference_between_interactions_significant = t_test_for_difference_of_means( list_of_thompson_user_clicks, list_of_ucb_user_clicks, 
                                                                                       mu_thompson, mu_ucb, s_thompson, s_ucb, total_data_pts_thompson, total_data_pts_ucb 
                                                                                    )

    return bool_difference_between_interactions_significant






collection_of_users = initialize_user_collection( TOTAL_USERS_PER_POPULATION, list_of_population_types = ["random", "thompson", "ucb"], list_of_divisions = DIVISIONS )

print("total users", len(collection_of_users))

generate_interaction_data_from_multiple_runs( collection_of_users, "thompson", TOTAL_TRIALS_PER_USER, USER_BIAS_TOWARD_DIVISIONS  )
generate_interaction_data_from_multiple_runs( collection_of_users, "ucb", TOTAL_TRIALS_PER_USER, USER_BIAS_TOWARD_DIVISIONS  )
generate_interaction_data_from_multiple_runs( collection_of_users, "random", TOTAL_TRIALS_PER_USER, USER_BIAS_TOWARD_DIVISIONS  )

# print(temp_list_of_users[0], "The first user ID")
# division_info_random_for_final_user = collection_of_users[temp_list_of_users[0]-1].get_division_info_random()


# print(division_info_random_for_final_user)



bool_algo_type_affects_user_decisions = check_if_algorithm_type_affects_user_decisions( collection_of_users, 
                                                                                        TOTAL_TRIALS_PER_POPULATION, 
                                                                                        list_of_population_types = ["random", "thompson", "ucb"] )

print(bool_algo_type_affects_user_decisions)



bool_difference_between_interactions_significant = check_for_significant_difference_between_clicks_due_to_algo_type( collection_of_users )

print( bool_difference_between_interactions_significant )



