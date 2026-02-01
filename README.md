# Football Performance Analytics

**Investigating the link between high-intensity running and team success using GPS tracker data.** 

This repository contains the full research report ([paper.pdf]) and supporting explanations of the system, methodology, and findings.

[paper.pdf]:https://github.com/idotalk/HG-Runs-Vs-xG/blob/master/paper.pdf

## Overview

This project explores a question that surprisingly has received almost no structured, data-driven research:

Does high-intensity running (Zone 5/6 speeds) directly correlate with team success in professional football?

Using two full seasons of Maccabi Haifa FC match data, GPS tracking, and advanced statistical modeling, this project builds an end-to-end analytical pipeline to quantify this relationship and evaluate its predictive value.

The work combines software engineering, data engineering, and sports analytics research to open new ways of thinking about performance indicators in football.

## Main Components
### 1. Data Pipeline

Built to process, align, and unify data from multiple sources:

* STATSports APEX GPS (high-frequency player tracking)

* OPTA event & xG data

* SofaScore lineup & metadata

* Official matches video

This pipeline was designed specifically to test the hypothesis about high-intensity running and team success, and to produce engineered features for predictive modeling.

### 2. Monte Carlo Simulator

A custom simulator that transforms xG timelines into expected points (xPts).
It uses 10,000 Bernoulli based simulations per match to estimate outcome distributions and produces results that align closely with real league tables.

This provides a new angle for evaluating dominance and match performance compared to raw results.

### 3. Visualization Tool

A tool that visualizes GPS based player movement on a normalized football pitch for analysis and validation.

## Methodology

The project includes:

* Feature engineering for zone based speed measures

* Correlation analysis using Pearson, Spearman and mutual information

* Train and test experiments with various models:

    * Linear regression

    * Decision trees

    * Random Forest

    * XGBoost

## Findings
All details, experiments and statistical results appear in [paper.pdf]

## Future Work

Possible extensions include adding more seasons, incorporating opponent tracking data and building advanced predictive models.


## Collaboration With Maccabi Haifa FC

The project was developed in cooperation with the performance staff at Maccabi Haifa FC.
Their collaboration included access to GPS data, expert interpretation of physical metrics and validation of the research findings.
