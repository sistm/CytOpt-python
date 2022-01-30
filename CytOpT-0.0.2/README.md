# CytOpt

## Description
The CytOpt is new package includes a new algorithm using regularized optimal transport to directly estimate the different cell population proportions from a biological sample characterized with flow cytometry measurements. Algorithm is based on the regularized Wasserstein metric to compare cytometry measurements from different samples, thus accounting for possible mis-alignment of a given cell population across sample (due to technical variability from the technology of measurements).
## Overview
The methods implemented in this package are detailed in the following
article:

> Paul Freulon, Jérémie Bigot, Boris P. Hejblum.
> CytOpT: Optimal Transport with Domain Adaptation for Interpreting Flow Cytometry data
> https://arxiv.org/abs/2006.09003

## Getting started

### Install CytOpT
Install the **CytOpT** package from pypi as follows:

```
pip install -r requirements.txt
pip install CytOpT # pip3 install CytOpT
```

## Example

### Packages

```
from CytOpT.CytOpT import CytOpt
```


### Preparing data

```
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

theta_true = np.zeros(10)

for k in range(10):
    theta_true[k] = np.sum(Lab_target == k + 1) / len(Lab_target)
```
### Comparison of methods
#### Steps
###### Classification using optimal transport with reweighted proportions. 
###### The target measure  𝛽  is reweighted in order to match the weight vector  ℎ̂   estimated with  𝙲𝚢𝚝𝙾𝚙𝚝.
###### Approximation of the optimal dual vector u. In order to compute an approximation of the optimal transportation plan, we need to approximate  𝑃𝜀 .
###### Class proportions estimation with  𝙲𝚢𝚝𝙾𝚙𝚝 Descent-Ascent procedure Setting of the parameters
###### Minmax swapping procedure. Setting of the parameters
###### Plot all Bland-Altman


```
from CytOpT import Cytopt

CytOpt(X_source, X_target, Lab_source, Lab_target=None, cell_type=None,
                              method="comparison_opt", theta_true=theta_true, eps=1e-04, n_iter=4000, power=0.99,
                              step_grad=50, step=5, lbd=1e-04, n_out=1000, n_stoc=10, n_0=10,
                              n_stop=1000, monitoring=False, minMaxScaler=True)
```

### CytOpT Minmax or Desasc 
```
from CytOpT import cytopt_minmax, cytopt_desasc

cytopt_desasc(X_source, X_target, Lab_source, eps=0.0001, n_out=4000, n_stoc=10, step_grad=50, const=0.1, theta_true=0)

cytopt_minmax(X_source, X_target, Lab_source,eps=0.0001, lbd=0.0001, n_iter=4000,
                  step=5, power=0.99, theta_true=0, monitoring=False)
                  
/// Or use CytOpt function with specified method parameter
```

## Urls
###### https://arxiv.org/abs/2006.09003