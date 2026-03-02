##How I started

i planned to do this project using flask framework (because i have prior experience in flask).so i have decided to build a laptop selection decision companion system.
There should be list of predefined laptops with specifications(optional).
the user could input custom inputs and the user could mention the features they priortize on.
the input data will be converted to numerical data.normalisation and weights should be added appropriatly.finally we should rank the laptop according to their final score.

The first working prototype had five engine files and could produce a ranked list from a budget input.

How my thinking evolved


I considered about getting the final score by just calculating according to the weights, later i understood about the role of normalisation in the process.
normalisation will make it easily comparable make it in a range between 0 and 1.
by normalisation we can adjust the importance of the specific parameters.
For Example for battery the higher battery life is optimal and for price the lower the price the more satisfactory it gets.
i made criteria.json which defined what is the type of the input,whether it is beneficial or cost
It is related to the normalisation part
where in the beneficial case as the value of ram is higher a high value is allotted
where in the cost case the as the value of weight is lower a high value is allotted>

version 1

intial there were only 5 components in the engine part
1)loader.py - to load the predefined data from the json file
2)normalisation.py - to normalise the values.
3)scorer.py- to do the weight multiplication
4)ranker.py-to find out the ranks of the laptops
5)explain.py-to give a explanation about the approach.

These files where part of the engine of the first prototype.
In the first details of the laptop was stored as a numerical number.
the specifications of the custom laptops were also collected as a numerical value
it will make confusions in respect to the user 
suppose if the user is purchasing a laptop and if he want to refer this site.
what is he supposed to do if asked about the score of the gpu.

version 2

so i decided to use real world data as input
modified the laptops.json so that it contains details about the storage,ram,gpu,etc.

eg:
   CPU: "Intel Core i7-1355U"
   GPU: "RTX 4060"
   RAM: "16GB"
   Storage: "512GB NVMe"
   Display: "2560x1600 IPS 165Hz"

There were some terms in which we can't give a proper comparison.
in the terms of ram we can easily compare it like
16gb>4gb
but in the case of gpu we can't compare it directly

so i created the file spec_maps.json ,it contains  nested json objects.
Each specification was mapped to a numerical value under their respective section

for eg:
rtx 4090:100
rtx 4070:70

the spec_mapper.py was created to automatically map spec to score

The processor input was missed in this version and it was rectified and processor details were added to the files

Version 3

The weight allocation system was not limited.which meant a user could give weights with no   limits.To counter this problem I redesigned this into a budget of 100 points distributed across all criteria

this idea was inspired from a game known as e football(pes)
where the player progression point can be used increase the stats of the player.
so the 100 weight points was divided between the features.Exceeding 100 weight points disable the user to get recommendations.

profile System

profiles.json has made to make pre set weight templates
it has been made so that it improves the user experiences.
After clicking the get recommendation button the user will get the best laptop
It also finds the best laptop for office as well gaming in that budget(applies to only predefined)

3-Mode Data Collection

The final version supports three dataset modes:
Predefined only — rank only the 12 built-in laptops
Custom only — rank only the laptops the user added
Combined  — rank everything together


Alternative approaches considered

i have thought about implementing a database.
I did'nt implement it beacuse we are priortising more on the custom laptop input rather than that of the predefined one.Moreover a simple json file will satsfy our requirements.

Had the idea about using ai for the data collection part by using a query.
dropped it because of the technical difficulties.

Refactoring decisions

The processor input was added later,when all other inputs have been mapped and ready to use.
while replacing the cpu perfromance score with the cpu.there where some key errors.
Also after correcting it there where pre stored scores for the predefined laptops
and the mapped scores for the custom laptop.It meant that same processor has different values.This was refactored so that cpu_score is always derived by calling map_cpu() on the cpu string field.


Absolute paths in app.py
The early version used relative file paths (open("data/laptops.json")). On Render, the working directory at gunicorn startup is not the project directory, so these paths failed silently. All file paths were refactored to use os.path.dirname(os.path.abspath(__file__)) as a BASE_DIR anchor.



Mistakes and corrections

When adding the performance input there was a cpu_score key mismatch.
the actual key was cpu.It was fixed later on

So after testing some test cases i found out that by choosing a gaming laptop profile it sometimes recommends macbook.
It was due to the gpu scores.
so i decided to covert that section to gaming/performance section 
for gaming laptops with high end graphics card is better
for editing purposes a good mac book is better


What changed during development and why

1) changed numeric specs to real world specs: Users know processor names, not benchmark scores

2) Added spec_maps.json and spec_mapper.py: To translate the real world specs to numeric values.

3) Replaced per-slider weights with 100-point budget: prevent meaningless weight allocation

4) added 3 mode dataset collection : providng users more freedom of data selection

5) added category winner: added category winner for office and gaming laptops.
