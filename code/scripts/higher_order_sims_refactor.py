import numpy as np
import pandas as pd
from scipy.linalg import toeplitz
import sys
import os
from config import config
import timecorr as tc
import nltools
from matplotlib import pyplot as plt
import seaborn as sns

cond= sys.argv[1]
r = sys.argv[2] #reps

F = int(sys.argv[3]) #number of features
T = int(sys.argv[4]) #number of timepoints
K = 2 #order

fname = cond + '_' + str(F) + '_' + str(T) + '_' + str(K)

width = 500

results_dir = os.path.join(config['resultsdir'], 'higher_order_sims_search', cond + '_' + str(T)+ '_' + str(F))

try:
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
except OSError as err:
   print(err)


def expanded_vec2mat(v):
  m = tc.vec2mat(v)
  x = np.zeros([v.shape[0], m.shape[0] ** 2])
  for t in range(m.shape[2]):
    x[t, :] = m[:, :, t].ravel()
  return x


laplace = {'name': 'Laplace', 'weights': tc.laplace_weights, 'params': {'scale': width}}
gaussian = {'name': 'Gaussian', 'weights': tc.gaussian_weights, 'params': {'var': width}}

eye_params = {}

def eye_weights(T, params=eye_params):
    return np.eye(T)

def generate_templates(order=1, **kwargs):
  kwargs['return_corrs'] = True
  _, next_template = tc.simulate_data(**kwargs)

  T = kwargs['T']
  templates = []
  for n in range(order - 1):
    print(n)
    templates.append(next_template)

    expanded_corrmats = tc.vec2mat(next_template)
    K2 = expanded_corrmats.shape[0] ** 2
    next_template = np.zeros([K2, K2, T])
    for t in range(T):
      x = expanded_corrmats[:, :, t]
      next_template[:, :, t] = np.kron(x, x)
    next_template = tc.mat2vec(next_template)
  templates.append(next_template)
  return templates


def generate_templates_refactor(order=1, cov_list=None, **kwargs):
  kwargs['return_corrs'] = True

  T = kwargs['T']
  templates = []
  for n in range(order):
      print(n)

      if cov_list:
          kwargs['datagen'] = cov_list[n]

      _, next_template = tc.simulate_data(**kwargs)


      if n >= 1:
          expanded_corrmats_last = tc.vec2mat(templates[n-1])
          expanded_corrmats_next = tc.vec2mat(next_template)

          K2 = expanded_corrmats_last.shape[0] ** 2

          next_template = np.zeros([K2, K2, T])

          for t in range(T):
              x_last = expanded_corrmats_last[:, :, t]
              x_next = expanded_corrmats_next[:, :, t]
              next_template[:, :, t] = np.kron(x_last, x_next)
          next_template = tc.mat2vec(next_template)

      templates.append(next_template)

  return templates


def generate_data(templates):
    order = len(templates) + 1
    adjusted_templates = [templates[-1]]  # generate adjusted templates in reverse order
    next_corrmats = adjusted_templates[-1]

    for n in range(order - 1, 1, -1):
        print(n)
        corrmats = tc.vec2mat(next_corrmats)
        K = corrmats.shape[0]
        sK = int(np.sqrt(K))
        T = corrmats.shape[2]

        draws = np.zeros([sK, sK, T])
        means = tc.vec2mat(templates[n - 2])


        for t in range(T):
            draws[:, :, t] = np.reshape(np.random.multivariate_normal(means[:, :, t].ravel(), corrmats[:, :, t]),
                                        [sK, sK])

        next_corrmats = tc.mat2vec(draws)
        adjusted_templates.append(next_corrmats)

        # try_it = np.random.multivariate_normal(np.zeros([sK * sK]), np.eye(sK * sK), size=T)
        # for t in range(T):
        #
        #     #x_hat = np.random.multivariate_normal(means[:, :, t].ravel(), corrmats[:, :, t]).reshape(sK, sK, order='A')
        #     #x_hat = np.random.multivariate_normal(np.zeros([sK * sK]), corrmats[:, :, t]).reshape(sK, sK, order='A')
        #     #x_hat = np.random.multivariate_normal(np.zeros([sK * sK]), np.eye(sK * sK))
        #
        #     try_c = corrmats[:, :, t]
        #     #try_c = nearPSD(try_c)
        #     #sns.heatmap(try_c)
        #     np.fill_diagonal(try_c, 10)
        #     c = np.linalg.cholesky(try_c)
        #
        #     # #sns.heatmap(c)
        #     # np.fill_diagonal(c, 0)
        #     # c /= np.max(np.abs(c))
        #     #
        #     # ## this increases the recovery performance by A LOT
        #     # np.fill_diagonal(c, 1)
        #     c = tc.helpers.norm_mat(c)
        #
        #     #sns.heatmap(c)
        #     x_hat = np.dot(try_it[t], c)
        #     #sns.heatmap(x_hat)
        #     x_hat = np.reshape(x_hat, [sK, sK])
        #     x_t = x_hat * x_hat.T
        #     x_t /= np.max(np.abs(x_t))
        #     #sns.heatmap(x_t)
        #     np.fill_diagonal(x_t, 1)
        #     draws[:, :, t] = x_t
        #
        #     # draws[:, :, t] = np.reshape(np.random.multivariate_normal(means[:, :, t].ravel(), corrmats[:, :, t]),
        #     #                             [sK, sK])
        #
        # next_corrmats = tc.mat2vec(draws)
        # adjusted_templates.append(next_corrmats)

    corrmats = tc.vec2mat(next_corrmats)
    K = int(corrmats.shape[0])
    T = corrmats.shape[2]
    data = np.zeros([T, K])

    for t in range(T):
        data[t, :] = np.random.multivariate_normal(np.zeros([K]), corrmats[:, :, t])

    adjusted_templates.reverse()
    return data, adjusted_templates


save_file = os.path.join(results_dir, str(r))

if not os.path.exists(save_file):

    recovery_performance_all = pd.DataFrame()

    templates = generate_templates(order=K, S=1, T=T, K=F, datagen=cond)
    #templates = generate_templates_refactor(order=K, cov_list=['blocky', 'toeplitz'], S=1, T=T, K=F, datagen=cond)

    # t_mat_1 = tc.vec2mat(templates[0])
    # t_mat_2 = tc.vec2mat(templates[1])
    # t_mat_new_1 = tc.vec2mat(templates_new[0])
    # t_mat_new_2 = tc.vec2mat(templates_new[1])

    data, adjusted_templates = generate_data(templates)

    get_f = lambda y: int((1/2) * (np.sqrt(8*y + 1) - 1)) #solve for x in y = ((x^2 - x)/2) + x


    recovery_performance = pd.DataFrame(index=np.arange(T), columns=np.arange(1, K+1))
    recovery_performance.index.name = 'time'
    recovery_performance.columns.name = 'order'
    recovery_performance_adj_temps = pd.DataFrame(index=np.arange(T), columns=np.arange(1, K+1))
    recovery_performance_adj_temps.index.name = 'time'
    recovery_performance_adj_temps.columns.name = 'order'
    next_data = data
    recovered_corrs_raw = []
    recovered_corrs_smooth = []

    for k in np.arange(1, K+1):
      #next_recovered_smooth = tc.timecorr(next_data, weights_function=laplace['weights'], weights_params=laplace['params'])
      next_recovered_smooth = tc.timecorr(next_data, weights_function=gaussian['weights'],weights_params=gaussian['params'])
      next_recovered_raw = tc.timecorr(next_data, weights_function=eye_weights, weights_params=eye_params)
      recovered_corrs_smooth.append(next_recovered_smooth)
      F_new = get_f(next_recovered_smooth.shape[1])
      for t in np.arange(T):
        recovery_performance.loc[t, k] = np.corrcoef(templates[k-1][t, F_new:], next_recovered_smooth[t, F_new:])[0, 1]
        recovery_performance_adj_temps.loc[t, k] = np.corrcoef(adjusted_templates[k - 1][t, F_new:], next_recovered_smooth[t, F_new:])[
            0, 1]



      if k == 1:

          # norm next data correlations
          try_norm = np.corrcoef(next_data.T)
          np.fill_diagonal(try_norm, 0)
          try_norm /= np.max(np.abs(try_norm))
          np.fill_diagonal(try_norm, 1)

          #sns.heatmap(try_norm)

        # heatmap of smooth first order corrs
          try_expand = expanded_vec2mat(next_recovered_smooth)
          #sns.heatmap(np.corrcoef(try_expand.T))

    # heatmap of raw first order corrs
      #plt.clf()
      #sns.heatmap(tc.vec2mat(templates[k-1][10]))
      #plt.show()


      next_data = expanded_vec2mat(next_recovered_raw)

    # recovery_performance.columns = [str(x + 1) for x in np.arange(K)]
    # recovery_performance['iteration'] = int(r)
    # recovery_performance_all = recovery_performance_all.append(recovery_performance)

    print(recovery_performance)
    plt.clf()
    plt.plot(recovery_performance[1])
    plt.plot(recovery_performance[2])
    plt.show()
    recovery_performance.to_csv(save_file + '.csv')

# if not os.path.isfile(save_file + '.csv'):
#     recovery_performance.to_csv(save_file + '.csv')
# else:
#     append_iter = pd.read_csv(save_file + '.csv', index_col=0)
#     append_iter = append_iter.append(recovery_performance)
#     append_iter.to_csv(save_file + '.csv')

