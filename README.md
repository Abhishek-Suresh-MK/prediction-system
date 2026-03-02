# Your understanding of the problem

So we have told about building a decision companion system.
A particular type of decision companion system has not been mentioned in the mail.
Any type of decision companion system can be made as per user's will.
So i have decided to build a laptop selection decision companion system.
There should be list of predefined laptops with specifications.
The user could input custom inputs and the user could mention the features they priortize on.
the input data will be converted to numerical data.
Normalisation and weights should be added appropriately.final we should rank the laptop according to their final score.


# Assumptions made

Specifications chosen are: CPU, GPU, RAM, Storage, Battery life, Weight, Display quality, and Price.
Hardware internals like core count, thread count, and clock speed were excluded in this version because they are harder for average users to interpret and compare.

The user does not want to know about the best laptop slightly out of budget.
budget filtering system is applied so only bes laptop within the budget is recommended

The JSON File would act as a sufficient datastore method.Using a database would increase the complexity and might be a overkill.

Processors,gpus etc are given numerical value representation out of 100 based on their perfromance compared to others of the same category.

Why you structured the solution the way you did

For easier build, I am starting at small scale.
I am starting with basic implementation of the system using the basic inputs.
no ai is used,only pure mathematical algorithm is used to predict the results.

Data Flow:
1)user enters the input weights and input custom laptops
2)system loads the laptop data(user defined only,pre defined,combined)
3)initial budget filtering
4)normalization is performed
5)weighted scoring is applied
6)ranking is generated
7)result is provided.

loader.py : Load predefined laptops, validate custom inputs, merge datasets
spec_mapper.py: Translate real-world spec strings into numeric scores
normalisation.py: Min-Max normalise all scores into a 0–1 range
scorer.py: Multiply normalised scores by user weights to produce a final 
scoreranker.py: Sort laptops by final score, assign ranks, find category champions
explain.py: Generate a human-readable breakdown of why the top laptop won

pipeline

User Input (budget + weights + optional custom laptops)
        │
        ▼
  LaptopLoader — loads laptops.json + merges custom entries
        │
        ▼
  Budget Filter — removes all laptops above budget
        │
        ▼
  SpecMapper.enrich_laptop — maps CPU/GPU/RAM/etc. strings → numeric scores
        │
        ▼
  LaptopNormalizer — Min-Max normalises each criterion across the pool
        │
        ▼
  LaptopScorer — applies user weights, computes weighted_sum = final_score
        │
        ▼
  rank_laptops — sorts descending, assigns rank 1, 2, 3…
        │
        ▼
  generate_explanation — produces structured breakdown for the top laptop
        │
        ▼
  JSON response → rendered in index.html

100 weight point is allocated among the features

calculation
beneficiary: normalised = (value - min_in_pool) / (max_in_pool - min_in_pool)
cost: normalised = (max_in_pool - value) / (max_in_pool - min_in_pool)

final_score = Σ (normalised_score_i × weight_i / 100)

# Design Decisions and trade-offs

Static spec mapping (JSON instead of live API)
We use a static spec_maps.json file to assign CPU and GPU scores.
This works offline and is fast.
However, it must be updated manually when new hardware releases.

Min-Max normalization instead of Z-score
We use Min-Max normalization to scale values between 0 and 1.
This makes the final score easy to understand.
Z-score handles outliers better but is harder to explain and display.

No database used
The dataset is small and read-only.
Using a database would add unnecessary complexity.
JSON files are enough for this project.

# Edge Cases Considered

Budget of zero 
1) No laptops within budget — the response indicates zero results and no recommendation is made.
2) Weights not summing to 100 — the frontend disables the submit button
3) Custom laptop with missing fields — loader.py validates all required fields and raises a descriptive ValueError before any processing begins.
4) All laptops identical on a criterion — Min-Max normalisation would produce 0/0; this is handled by defaulting all normalised values to 0.5 (midpoint) when max equals min.
5) Single laptop in pool — the explainer handles pools of size 1 gracefully (no "beat #2" comparison is generated).



Edge cases considered
initial budget filtering is done to avoid unecessary comparison.

# How to run the project

### Clone the repository
git clone https://github.com/Abhishek-Suresh-MK/vonnue-laptop-decision-companion
cd vonnue-laptop-decision-companion/Source_Code

### Install dependencies
pip install -r requirements.txt

#### Run the app
python app.py

# host link: https://laptopiq-cwbx.onrender.com/

# What you would improve with more time

1) Add more parameters like refresh rate,thermal performance etc
2) make a bigger live database so that the user can easily select the laptop version instead of entering the specs.
3) complete custom laptop building decider

What you would improve with more time

1) Add more parameters like refresh rate,thermal performance etc
2) make a bigger live database so that the user can easily select the laptop version instead of entering the specs.
3) complete custom laptop building decider

