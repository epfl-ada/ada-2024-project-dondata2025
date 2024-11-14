import scipy.stats as stats
import numpy as np

#Check if a distribution is normal or not.
def check_normality(data):
    # Drop NaN and infinite values
    clean_data = data.dropna()
    clean_data = clean_data[np.isfinite(clean_data)]

    result = stats.anderson(clean_data, dist='norm')
    print(f'Anderson-Darling Test Results:')
    print(f'  Statistic: {round(result.statistic, 3)}')
    print(f'  Critical Values: {result.critical_values}')
    print(f'  Significance Levels: {result.significance_level}')
    if result.statistic < result.critical_values[2]:  # Using the 5% significance level
        print('  Conclusion: Data looks Gaussian (fail to reject H0)')
    else:
        print('  Conclusion: Data does not look Gaussian (reject H0)')


#Check if a distribution is skewed or not.
def check_skewness(data):

    print('The skewness score is:', data.skew(),':')
    if data.skew() > 0:
        print('the distribution is right skewed')
    elif data.skew() < 0:
        print('the distribution is left skewed')
    else:
        print('the distribution is symmetric')

