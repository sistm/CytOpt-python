# Copyright (C) 2021, Paul Freulon <paul.freulon@math.u-bordeaux.fr>=
#
# License: MIT (see COPYING file)


import numpy as np
import pandas as pd
from scipy.stats import entropy

__all__ = ['cytopt_desasc', 'Label_Prop_sto']


def cost(X_s, y):
    """
    Squared euclidean distance between y and the I points of X_s.
    """
    diff = X_s - y
    return np.linalg.norm(diff, axis=1) ** 2


def diff_simplex(h):
    """
    Computation of the Jacobian matrix of the softmax function.
    """
    try:
        h = np.array(h, np.float)
    except Exception as e:
        print(e)
    K = len(h)
    Diff = np.zeros((K, K), dtype=float)
    for i in range(K):
        for j in range(K):
            if i == j:
                Diff[i, j] = (np.exp(h[i]) * np.sum(np.exp(h)) - np.exp(2 * h[i])) / (np.sum(np.exp(h)) ** 2)
            else:
                Diff[i, j] = - np.exp(h[i] + h[j]) / (np.sum(np.exp(h)) ** 2)
    return (Diff)


def grad_h(f, X_s, y, alpha, eps=0):
    """
    This function calculates the gradient of the function that we aim to maximize.
    The expectation of this function computed at a maximizer equals the wasserstein disctance,
    or its regularized counterpart.
    """
    if eps == 0:
        cost_y = cost(X_s, y)
        i_star = np.argmin(cost_y - f)
        to_return = alpha.copy()
        to_return[i_star] = alpha[i_star] - 1
        return (to_return)

    else:
        arg = (f - cost(X_s, y)) / eps
        Mx = np.max(arg)
        pi = np.exp(arg - Mx)
        pi = pi / pi.sum()
        return alpha - pi


def gammatrix(X_s, Lab_source):
    """
    Computation of the operator D that maps the class proportions with the weights.
    """
    I = X_s.shape[0]
    if min(Lab_source) == 0:
        K = int(max(Lab_source))
        D = np.zeros((I, K + 1))
        for k in range(K + 1):
            D[:, k] = 1 / np.sum(Lab_source == k) * np.asarray(Lab_source == k, dtype=float)

        h = np.ones(K + 1)

    else:
        K = int(max(Lab_source))
        D = np.zeros((I, K))
        for k in range(K):
            D[:, k] = 1 / np.sum(Lab_source == k + 1) * np.asarray(Lab_source == k + 1, dtype=float)

        h = np.ones(K)
    return (D, h)


def Robbins_Wass(X_s, X_t, alpha, beta, eps=0, const=0.1, n_iter=10000):
    """
    Function that calculates the approximation of the Wasserstein distance between mu and nu
    thanks to the Robbins-Monro Algorithm. X and Y are the supports of the source and target
    distribution. Alpha and beta are the weights of the distributions.
    """
    n_iter = int(n_iter)
    I = X_s.shape[0]
    J = X_t.shape[0]

    alpha = alpha.ravel()

    # Step size policy.
    if eps == 0:
        gamma = 0.01 / (4 * np.min(alpha))
    else:
        gamma = eps / (1.9 * min(alpha))
    c = 0.51
    # Sampling with respect to the distribution beta.
    sample = np.random.choice(a=np.arange(J), size=n_iter, p=beta.ravel())

    # Initialization of the dual vector f.
    f = np.zeros(I)

    # f_I vector:useful for the unregularized case.
    F_I = 1 / np.sqrt(I) * np.ones(I)

    for k in range(n_iter):

        # One sample of the beta distributions.
        y = X_t[sample[k], :]

        # Computation of the gradient if eps>0 or subgradient if eps=0.
        if eps == 0:
            grad_temp = grad_h(f, X_s, y, alpha)
            grad = (grad_temp - const * np.sum(f * F_I) * F_I)
        else:
            grad = grad_h(f, X_s, y, alpha, eps=eps)

        # Update of the dual variable
        f = f + gamma / ((k + 1) ** c) * grad

    return f


# cytopt
def cytopt_desasc(X_s, X_t, Lab_source, eps=0.0001, n_out=4000, n_stoc=10, step_grad=50, const=0.1, theta_true=0):
    """
    Function that estimates the class proportions in the target data set.
    It solves the minimization problem with a gradient descent method.
    At each iteration, a (sub)gradient of W^{eps}(alpha, beta) is approximated with stochastic optimization
    Techniques.
    """

    print('\n Epsilon: ', eps)
    I, J = X_s.shape[0], X_t.shape[0]

    # Definition of the operator D that maps the class proportions with the weights.
    D, h = gammatrix(X_s, Lab_source)

    # Weights of the target distribution
    beta = 1 / J * np.ones(J)

    # Storage of the KL between theta_hat and theta_true
    KL_Storage = np.zeros(n_out)

    for it in range(n_out):
        prop_classes = np.exp(h) / np.sum(np.exp(h))
        Dif = diff_simplex(h)
        alpha_mod = D.dot(prop_classes)

        # Computation of the gradient:
        grad = Robbins_Wass(X_s, X_t, alpha_mod, beta, eps=eps, const=const, n_iter=n_stoc)
        h = h - step_grad * (np.transpose(D.dot(Dif))).dot(grad)
        prop_classes_new = np.exp(h) / np.sum(np.exp(h))

        if it % 100 == 0:
            print('Iteration ', it, ' - Curent h_hat: \n', prop_classes_new)

        KL_Loss = entropy(pk=prop_classes_new, qk=theta_true)
        KL_Storage[it] = KL_Loss

    return [prop_classes_new, KL_Storage]


if __name__ == '__main__':
    # Source Data
    Stanford1A_values = pd.read_csv('../tests/data/W2_1_values.csv',
                                    usecols=np.arange(1, 8))
    Stanford1A_clust = pd.read_csv('../tests/data/W2_1_clust.csv',
                                   usecols=[1])

    # Target Data
    Stanford3A_values = pd.read_csv('../tests/data/W2_7_values.csv',
                                    usecols=np.arange(1, 8))
    Stanford3A_clust = pd.read_csv('../tests/data/W2_7_clust.csv',
                                   usecols=[1])

    X_source = np.asarray(Stanford1A_values)
    X_target = np.asarray(Stanford3A_values)
    Lab_source = np.asarray(Stanford1A_clust['x'])
    Lab_target = np.asarray(Stanford3A_clust['x'])

    cytopt_desasc(X_source, X_target, Lab_source, eps=0.0001, n_out=4000, n_stoc=10, step_grad=50, const=0.1,
                  theta_true=0)
