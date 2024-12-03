# Model Evaluation

CS 6220, Group 25

Georgia Institute of Technology

Fall 2024

## Introduction

This directory contains the source code for and results of the model finetuning and evaluation for this project. This ReadMe will briefly describe the fine-tuning process of each chosen model and provide a description of the contents of the directory.

## Contents

- [Model Evaluation](#model-evaluation)
  - [Introduction](#introduction)
  - [Contents](#contents)
  - [Fine Tuning Descriptions](#fine-tuning-descriptions)
  - [Directory Overview](#directory-overview)

## Fine Tuning Descriptions

For this project, we tuned an ensemble of 5 different language models on SEC-10K filing data for publicly traded companies. We then evaluated their ability to answer financial advisory questions against our bespoke [ground truth dataset](./evaluation_dataset.csv).

The ground truth data and results have also been published [here](https://huggingface.co/datasets/iamwillferguson/StockSensei_Ground_Truth/blob/main/README.md).

More details about the individual hyperparameters for each model can be found in our demo slides [here](https://docs.google.com/presentation/d/1g2gA1GKPQRnH1-bUfHatQFqQkllJdWV2MXaJEPwqoZ8/edit?usp=sharing).

- LLaMa 3.2-1B
  - Fine-Tuned By: Hersh Dhillon
  - Tuning Architecture: HuggingFace Transformers, Datasets, PACE (32GB)
- LLaMa 3.2-3B
  - Fine-Tuned By: Dorsa Ajami
  - Tuning Architecture: Unsloth, Colab (A100)
- Phi3-mini (0.5B Parameters)
  - Fine-Tuned By: Will Ferguson
  - Tuning Architecture: Unsloth, Ollama, Langchain, Colab (Tesla T4)
- Mistral-7b
  - Fine-Tuned By: Mathan Mahendran
  - Tuning Architecture: Unsloth, PACE (32GB)
- Gemini-1.5-Flash
  - Fine-Tuned By: Ayushi Mathur
  - Tuning Architecture: Google GenAI (API-based tuning)

## Directory Overview

Below is a description of this directory's other contents:

- [ft_scripts](./ft_scripts/): A folder containing the individual notebooks used to fine-tune the LLMs (since model weights are not contained in this repository, results can be replicated with these scripts)
- [individual_results](./individual_results/): A folder containing the fine-tuning output of each individual model against the ground truth data
- [evaluation_dataset.csv](./evaluation_dataset.csv): The ground-truth dataset
- [fine_tuning_results.csv](./fine_tuning_results.csv): The master file of all outputs against the ground truth
- [generate_ground_truth.ipynb](./generate_ground_truth.ipynb): The script used to create the ground truth dataset.
- [llm_as_a_judge.ipynb](./llm_as_a_judge.ipynb): The script used to evaluate the outputs using an LLM Judge
- [LLM_judge_results.csv](./LLM_judge_results.csv): A file contianing the results of the judging script