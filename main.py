import numpy
from tqdm import tqdm
import numpy
import pandas
import StochasticBanditsModules
import StochasticBanditsPolicies
import matplotlib.pyplot

horizon_vals = [25, 50, 75, 100, 125, 150, 175, 200]
N = 5000
K = 8

no_of_rounds = numpy.ceil(numpy.log(K) / numpy.log(2))

arm_mean_vectorized = numpy.vectorize(StochasticBanditsModules.arm_mean)
arm_empirical_mean_vectorized = numpy.vectorize(StochasticBanditsModules.arm_empirical_mean)
arm_posterior_mean_vectorized = numpy.vectorize(StochasticBanditsModules.arm_posterior_mean)
arm_priori_mean_vectorized = numpy.vectorize(StochasticBanditsModules.arm_priori_mean)
arm_variance_square_vectorized = numpy.vectorize(StochasticBanditsModules.arm_variance_square)
arm_posterior_variance_square_vectorized = numpy.vectorize(StochasticBanditsModules.arm_posterior_variance_square)

# Main Body of Code: Simulation Work

probability_array_freq = numpy.array([])
probability_array_bayes = numpy.array([])

for horizon in horizon_vals:

    sum_val_bayes = 0
    sum_val_freq = 0

    #   BayesElim2

    for index in tqdm(range(N)):

        # BayesElim2 Code:
        experiment_bayes = StochasticBanditsModules.Environment()
        # Careful!,  Import only priori arms otherwise priori_mean will be undefined
        for i in range(K):
            new_arm = StochasticBanditsModules.PrioriGaussianArm(experiment_bayes, 1 / (2 ** i))

        arms_bayes = experiment_bayes.listArms()
        arms_bayes_list = pandas.DataFrame(index=arms_bayes, data=arm_posterior_mean_vectorized(arms_bayes),
                                           columns=['posterior_mean'])
        optimal_mean_bayes = numpy.amax(arm_mean_vectorized(arms_bayes))

        for round_no in range(int(no_of_rounds)):

            sum_of_variance_square = numpy.sum(arm_variance_square_vectorized(arms_bayes_list.index))
            for arm in arms_bayes_list.index:
                no_of_pulls = horizon * arm.variance_square / (no_of_rounds * sum_of_variance_square)
                for i in range(int(no_of_pulls)):
                    arm.pullArm()
                no_of_samples = len(arm.history)
                arm.posterior_variance_square = 1 / (
                        (1 / arm.priori_variance_square) + (horizon / (no_of_rounds * sum_of_variance_square)))
                arm.posterior_mean = arm.posterior_variance_square * (
                        arm.priori_mean / arm.priori_variance_square + numpy.sum(arm.history) / arm.variance_square)

            arm_bayes_iterr_list = pandas.DataFrame(index=arms_bayes_list.index,
                                                    data=arm_posterior_mean_vectorized(arms_bayes_list.index),
                                                    columns=['posterior_mean'])

            arms_bayes_iterr_list = arm_bayes_iterr_list.sort_values(by='posterior_mean', ascending=False)

            arms_bayes_list = arms_bayes_iterr_list.head(int(len(arms_bayes_list.index) / 2))

        if arms_bayes_list.index[0].mean == optimal_mean_bayes:
            sum_val_bayes = sum_val_bayes + 1

    # Freq Code:
    for index in tqdm(range(N)):
        experiment_freq = StochasticBanditsModules.Environment()
        for i in range(K):
            new_arm = StochasticBanditsModules.PrioriGaussianArm(experiment_freq, 1 / (2 ** i))

        arms_freq = experiment_freq.listArms()
        arms_freq_list = pandas.DataFrame(index=arms_freq, data=arm_empirical_mean_vectorized(arms_freq),
                                          columns=['empirical_mean'])
        optimal_mean_freq = numpy.amax(arm_mean_vectorized(arms_freq))

        for round_no in range(horizon):

            for arm in arms_freq_list.index:
                for n in range(int(horizon / (len(arms_freq_list.index) * no_of_rounds))):
                    arm.pullArm()

            arms_freq_iterr_list = pandas.DataFrame(index=arms_freq_list.index,
                                                    data=arm_empirical_mean_vectorized(arms_freq_list.index),
                                                    columns=['empirical_mean'])
            arms_freq_iterr_list = arms_freq_iterr_list.sort_values(by='empirical_mean', ascending=False)
            arms_freq_list = arms_freq_iterr_list.head(int(len(arms_freq_list.index) / 2))

        if arms_freq_list.index[0].mean == optimal_mean_freq:
            sum_val_freq = sum_val_freq + 1

    probability_array_freq = numpy.append(probability_array_freq, 1 - (sum_val_freq / N))
    probability_array_bayes = numpy.append(probability_array_bayes, 1 - (sum_val_bayes / N))

# Plotting the results
matplotlib.pyplot.plot(horizon_vals, probability_array_bayes, label='BayesElim2')
matplotlib.pyplot.plot(horizon_vals, probability_array_freq, label='FreqElim2')
matplotlib.pyplot.xlabel('Horizon')
matplotlib.pyplot.ylabel('Probability of Misidentification of Optimal Arm')
matplotlib.pyplot.savefig('analysis.png')
