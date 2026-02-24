Your understanding of the problem

So we have told about building a decision companion system.A particular type of decision companion system has not been mentioned in the mail.Any type of decision companion system can be made as per user's will.
so i have decided to build a laptop selection decision companion system.
there should be list of predefined laptops with specifications.
the user could input custom inputs and the user could mention the features they priortize on.
the input data will be converted to numerical data.normalisation and weights should be added appropriatly.final we should rank the laptop according to their final score.


Assumptions made

the laptop selection criteria is not so hardware based(as of now)
we are adding parameters that involve performance,battery,weight


Why you structured the solution the way you did

For easier build, I am starting at small scale.


Data Flow:
1)user enters the input
2)system loads the predifined laptop data
3)merge with the user given laptop data
4)initial budget filtering
5)normalization is performed
6)weighted scoring is applied
7)ranking is generated
8)result is provided.


Design decisions and trade-offs

Edge cases considered
initial budget filtering is done to avoid unecessary comparison.

How to run the project

What you would improve with more time
