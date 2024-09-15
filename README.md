[![INFORMS Journal on Computing Logo](https://INFORMSJoC.github.io/logos/INFORMS_Journal_on_Computing_Header.jpg)](https://pubsonline.informs.org/journal/ijoc)

# A Data-Driven Optimization Framework for Static Rebalancing Operations in Bike Sharing Systems

This archive is distributed in association with the [INFORMS Journal on
Computing](https://pubsonline.informs.org/journal/ijoc) under the [MIT License](LICENSE).

The research data and Python scripts in this repository are a snapshot of the data and algorithms
used in the research reported on in the paper 
[A Data-Driven Optimization Framework for Static Rebalancing Operations in Bike Sharing Systems](https://doi.org/10.1287/ijoc.2021.0112) by Junming Liu, Weiwei Chen, and Leilei Sun. 

## Cite

To cite the contents of this repository, please cite both the paper and this repo, using their respective DOIs.

[https://doi.org/10.1287/ijoc.2022.0182](https://doi.org/10.1287/ijoc.2022.0182)

[https://doi.org/10.1287/ijoc.2022.0182.cd](https://doi.org/10.1287/ijoc.2022.0182.cd)


Below is the BibTex for citing this version of the code.

```
@article{liu2024ijoc,
  author =        {Junming Liu and and Weiwei Chen and Leilei Sun},
  publisher =     {INFORMS Journal on Computing},
  title =         {A Data-Driven Optimization Framework for Static Rebalancing Operations in Bike Sharing Systems},
  year =          {2024},
  doi =           {10.1287/ijoc.2022.0182.cd},
  url =           {https://github.com/INFORMSJoC/2022.0182},
  note =          {Available for download at https://github.com/INFORMSJoC/2022.0182}
}  
```
## Requirements

For this project, we use the following Python Packages:

1. Networkx is for the creation and study of the structrue, dynamics, and properties of network structure.
2. scikit-learn (v1.0.2) is a free software machine learning library for the Python programming language. It features various classification, regression and clustering algorithms.
3. NumPy (v1.19.5) is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays.
4. pandas (v1.3.5) is a software library written for the Python programming language for data manipulation and analysis. In particular, it offers data structures and operations for manipulating numerical tables and time series.
5. Gurobi 9.0.2 (linux64). The Gurobi Optimizer is a commercial optimization solver for linear programming (LP), quadratic programming (QP), quadratically constrained programming (QCP), mixed integer linear programming (MILP), mixed-integer quadratic programming (MIQP), and mixed-integer quadratically constrained programming (MIQCP).


## Description

This repository provides an end-to-end solution to the static rebalancing operations in bike sharing systems. The study uses the raw data of bike demand and station inventory status to generate the optimal rebalancing routes that reallocate system-wide bike inventories among stations during the night to maintain a high service level while minimizing demand loss due to stockout or overcapacity. The repository reports the raw data, algorithms, and extensive numerical experiments reported in the paper, using real-world data from New York City Citi Bike.

This repository includes three folders, **data**, **script**, and **results**

## Data files
The **data** folder contains a sample of the raw data used in the paper and different scales of case studies for the rebalancing optimization. Specifically, the folder contains the following data files:

1. 0-RawData: 3-month raw data of station-level bike demand and inventory status.
2. 1-DemandData: aggregated bike demand features with regional station inventory status.
3. 2-DataWeather: Data table with weather conditions for model inputs.
4. 3-1-SmallCase (SCA): Small case studies of size 15 - 19 for comparison of multi-visit and single-visit strategies. 
5. 3-2-MiddleCase: Medium case studies of size 20 - 35 for comparison of vMILP and SCA. 
6. 4-LargeCase: Large case study of the NYC Bike-sharing System.

## Script files

The **script** folder contains the core scripts used for data processing, prediction, and optimization. 

1. 0-Generate_AggregateDemand.py: generage aggregate demand (in 1-DemandData Folder) using raw dataset (in 0-RawData).
2. 1-CombineWeather.py: combine weather information and generate data table (in 2-DataWeather).
3. 2-Regression.py: a NARX model for demand prediction. Please revise the following configuration for the prediction of a specific time period demand.

```python
HOUR = 8 #hour of the day
PERIOD = 1 # period of the hour (1: first 30-minutes period; 2: second 30-minutes period)
WEEKDAY = True #(Weekday demand or weekend demand prediction)
HISTORICAL_WINDOW = 5 #(time lag. 5: for weekday prediction; 2: weekend prediction.)
TEST_HORIZON = 10 #(number of days for evaluation)
```
The following scripts are used for small and medium case studies:

4. 3-1-Multivisit_vMIP.py: vMIP model that supports multivisit strategy (Table 2).
5. 3-2-Singlevisit_vMIP.py: vMIP model that supports single visit strategy (Table 2).
6. 3-3-SCA.py, 3-3-SCA-middlecase.py: SCA heuristic model that supports multi-visit strategy (Tables 3, 4, E1, E2, E3, E4).

The following scripts are used for large case study.

1. 4-1-NYC LargeCase Codeserver.py: SCA heuristic model for the complete case study (Table F.1).
2. 4-2-NYC LargeCase visualization.py: visualization of the final rebalacing operation decisions (Figure F.1).


The **result** folder contains log files and final outputs of the scripts.

## Ongoing Development

This code is being developed on an on-going basis at the author's
[Github site](https://github.com/liujm8/IJOC-Bike).
