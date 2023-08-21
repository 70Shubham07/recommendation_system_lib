# utility functions
import random
from random import choices
import math

from scipy.stats import chi2_contingency
from scipy.stats import chi2
from scipy import stats
import numpy as np
from numpy.random import seed
from numpy.random import randn
from scipy.stats import shapiro



def sample_using_beta_distribution( division_info_thompson, divisions ):
    max_random = 0
    selected_division = ''


    for info_dict in division_info_thompson:

        random_beta = random.betavariate( info_dict["reward_one"]+1, info_dict["reward_zero"]+1 )

        if random_beta > max_random:
            max_random = random_beta
            selected_division = info_dict["division_name"]

    return selected_division



def recommendation_by_thompson( total_trials_so_far, user_bias_toward_divisions, divisions, division_info_thompson ):

    if total_trials_so_far == 0:
        
        recommended_division = random.choice( divisions )
        user_decision = choices( [1,0], user_bias_toward_divisions[recommended_division] )[0]


    else:

        recommended_division = sample_using_beta_distribution( division_info_thompson, divisions )
        user_decision = choices( [1,0], user_bias_toward_divisions[recommended_division] )[0]

        

    return recommended_division, user_decision






def recommendation_by_ucb( total_trials_so_far, user_bias_toward_divisions, divisions, division_info_ucb ):


    if total_trials_so_far == 0:

        recommended_division = random.choice( divisions )
        user_decision = choices( [1,0], user_bias_toward_divisions[recommended_division] )[0]


    else:

        max_upper_bound = 0
        recommended_division = ""
        for info_dict in division_info_ucb:
            if info_dict["times_selected"]>0:
                avg_reward = info_dict["rewards_so_far"]/info_dict["times_selected"]
                delta_I = math.sqrt(  (3/2 * math.log(total_trials_so_far + 1)) / ( info_dict["times_selected"] ) )
                upper_bound = avg_reward + delta_I

            else:
                upper_bound = 1e400
            if upper_bound > max_upper_bound:
                max_upper_bound = upper_bound
                recommended_division = info_dict["division_name"]

        user_decision = choices( [1,0], user_bias_toward_divisions[recommended_division] )[0]

    return recommended_division, user_decision


def recommendation_by_random(user_bias_toward_divisions, divisions, division_info_random):

    recommended_division = random.choice( divisions )
    user_decision = choices( [1,0], user_bias_toward_divisions[recommended_division] )[0]        

    return recommended_division, user_decision





def get_division_probabilities( divisions ):
    prob_high = 0.8
    prob_low = 0.2
    # division_weights = list() # in C++ it would be vector< vector<int> > divisionWeights; 
    division_weights = dict()
    for division in divisions:
        if division in ["NEW HOME MISC L1", "HOUSEHOLD", "GROCERY AND WHOLESALE", "PERISHABLE"]:
            division_weights[ division ] =  [prob_high, prob_low] 
        else:
            # 0.6/35. coz 0.4 goes to the above 4 divisions
            division_weights[ division ] =  [prob_low, prob_high] 

    return division_weights




def chi_squared_test_for_independence( population_type_2_total_clicks, total_trials_per_population ):
    # the 2 types of responses: clicked or not clicked
    r = 2

    # the 3 population types OR 3 tests 
    c = 3

    degrees_of_freedom = (r-1)*(c-1)

    # Creating the 2 by 3 contingency matrix
    clicked_list = [ population_type_2_total_clicks[ population_type ] for population_type in list( population_type_2_total_clicks.keys() )  ]
    not_clicked_list = [ total_trials_per_population - population_type_2_total_clicks[ population_type ]  for population_type in list( population_type_2_total_clicks.keys() ) ]

    contingency_matrix = [ clicked_list, not_clicked_list  ]

    print("Below is contingency matrix\n", contingency_matrix)

    # chi-squared test with similar proportions

    # contingency table
    # table = [   [10, 20, 30],
    #             [6,  9,  17]]
    stat, p, dof, expected = chi2_contingency(contingency_matrix)
    print('dof=%d' % dof)
    print(expected)
    
    # interpret test-statistic

    # prob 0.95 means 0.05 is level of significance
    prob = 0.95
    critical = chi2.ppf(prob, dof)
    print('probability=%.3f, critical=%.3f, stat=%.3f' % (prob, critical, stat))

    if abs(stat) >= critical:
        print('Dependent (reject H0)')
    else:
        print('Independent (fail to reject H0)')
    # interpret p-value

    alpha = 1.0 - prob
    print('significance=%.3f, p=%.3f' % (alpha, p))
    if p <= alpha:
        print('Dependent (reject H0)')
        return False
    else:
        print('Independent (fail to reject H0)')
        return True




# From http://docs.scipy.org/doc/scipy/reference/tutorial/stats.html

# As an exercise, we can calculate our ttest also directly without using the provided function, which should give us the same answer, and so it does:

# tt = (sm-m)/np.sqrt(sv/float(n))  # t-statistic for mean
# pval = stats.t.sf(np.abs(tt), n-1)*2  # two-sided pvalue = Prob(abs(t)>tt)
# print 't-statistic = %6.3f pvalue = %6.4f' % (tt, pval)
# t-statistic =  0.391 pvalue = 0.6955


def t_test_for_difference_of_means(list_of_thompson_user_clicks, list_of_ucb_user_clicks, mu_A, mu_B, s_A, s_B, total_sample_points_A, total_sample_points_B):


    #calculate std error first
    se = np.sqrt( (s_A**2)/total_sample_points_A + (s_B**2)/total_sample_points_B )

    # steps to calculate degrees of freedom.
    numerator_exp = ( (s_A**2)/total_sample_points_A + (s_B**2)/total_sample_points_B  ) ** 2

    denominator_exp = ( ( ( (s_A**2)/total_sample_points_A )**2 )/( total_sample_points_A-1 ) ) + ( ( ( (s_B**2)/total_sample_points_B )**2 )/( total_sample_points_B-1 ) )

    dof = numerator_exp/denominator_exp

    t_stat = ( (mu_A - mu_B) - 100 )/ se

    # pval = stats.t.sf(np.abs(tt), n-1)*2 -> This gives 2-sided p values.  Or   P(t < -tStat) + P( t > tStat )
    # pval = 1 - stats.t.sf(np.abs(t_stat), dof)
    pval = stats.t.sf(np.abs(t_stat), dof)
    print("t-stat is: ", t_stat, "pval is: ", pval)

    # t_stat, pval = stats.ttest_ind(list_of_thompson_user_clicks, list_of_ucb_user_clicks, equal_var = False)
    # print("t-stat is: ", t_stat, "pval is: ", pval)

    if pval > 0.05:
        print("Fail to reject H0. Difference is not statistically significant")
        return False

    else:
        print("Reject H0. Difference is statistically significant")
        return True






















