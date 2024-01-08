---
layout: article
title: 'Enhancing Echo State Network with Particle Swarm Bayesian Optimization Enabled Echo State Selection for Time Series Forecasting'
permalink: /under_review/psbesn.html
key: ur-psbesn
---
Xinze Zhang, Qi Sima, Kun He, Yukun Bao, and Shuhan Chen

<!--more-->

### Abstract

<div style="text-align: justify" markdown='1'>


Echo state network (ESN) has been widely employed for time series forecasting due to its remarkable efficacy. The dominant way to train an ESN-based prediction model is to calculate the output weights based on the mappings between the sequential echo states and targets, wherein a period of initial echo states is discarded to mitigate the effects of the zero initial state. This results in the loss of valuable information from the discarded initial states while retaining redundant echo state representations. In this regard, we propose a novel particle swarm bayesian optimization (PSBO) approach to provide an optimized ESN (PSBO-ESN) for time series forecasting, enabling the ESN model to adaptively select and retain more salient and indicative echo states. In PSBO-ESN, the solution to the echo state selection problem is encoded as a binary vector. The particle swarm optimization (PSO) algorithm is leveraged to explore the solution space globally, while a particle-specific bayesian optimization (BO) is designed to conduct the local search, thereby enhancing the exploitation ability of the proposed method.   Comprehensive experiments are conducted on two benchmark prediction tasks and a practical electricity load dataset. The results demonstrate that PSBO-ESN outperforms all baseline methods and strongly enhances the ESN model for time series forecasting.

<!-- Thus, feature selection is also an important issue in ESN, which directly affects the hidden state set, so as to impact the performance. 
To address these problems, a novel approach called ternary memetic algorithm based ESN (TMA-ESN) is proposed for time series forecasting, which provides a framework that unifies feature-state selection and parameter optimization of the ESN for time series forecasting. -->

</div>
