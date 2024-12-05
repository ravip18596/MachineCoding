```text
    Bill Sharing Application

Problem Definition
To create a bill sharing application(like splitwise). The application features are as follows

Group Creation
The application must have a concept of a group - which is basically a collection of registered users.
A registered user can belong to multiple groups.

Bill Creation
A person should be able to add a bill to the application. The bill will contain 
Total Amount of the bill.
People involved and their share of contribution. Share can be given as exact amount or percentages of total.
Group to which that bill get added

Tracking
The application should keep track of all such bills. Also, the application should be able to display two things: 
Total Balance to a user.
Group wise balances to a user.

Example
Mudit registers a bill for lunch totalling 300 rupees.
The bill is to be split equally among Mudit, Sourav and Souvik. 
Mudit has paid 250 while Souvik shelled out 50 rupees to complete the bill.

Shares of three are as follows

Mudit
Souvik
Sourav
Owes 150
Give 50
Give 100


Bonus
Attempt this only after completing the above requirements.

Support individual (person to person) balances. Also take care of concurrency issues that can arise out of multiple people registering bills at the same time.

Detailed Example
Person :
[
{
id: person1@xyz.com,
name: person1
},
{
id: person2@xyz.com,
name: person2
},
{
id: person3@xyz.com,
name: person3
}
]

Group:
[
    {
        id: group1,
        name: Group 1,
        members: [person1@xyz.com, person2@xyz.com] 
},
{
        id: group2,
        name: Group 2,
        members: [person2@xyz.com, person3@xyz.com] 
}
]

Bill: 
{
    desc: Bill 1,
    totalAmount: 300,
    groupId: group1,
    contribution: [{person: person1@xyz.com, share: 100},{person: person2@xyz.com, share: 200}],
    paidBy: [{person: person1@xyz.com, share: 300}]
}

{
    desc: Bill 2,
    totalAmount: 500,
    groupId: group1,
    contribution: [{person: person1@xyz.com, share: 250},{person: person2@xyz.com, share: 250}],
    paidBy: [{person: person2@xyz.com, share: 500}]
}


{
    desc: Bill 3,
    totalAmount: 100,
    groupId: group2,
    contribution: [{person: person2@xyz.com, share: 10},{person: person3@xyz.com, share: 90}],
    paidBy: [{person: person3@xyz.com, share: 100}]
}


{
    desc: Bill 4,
    totalAmount: 300,
    groupId: group2,
    contribution: [{person: person2@xyz.com, share: 150},{person: person3@xyz.com, share: 150}],
    paidBy: [{person: person3@xyz.com, share: 100},{person: person2@xyz.com, share: 200}]
}

Final Balance should look like this: 

Overall

Person
Balance
Person 1
-50
Person 2
90
Person 3
40


Group 1

Person
Balance
Person 1
-50
Person 2
50
Person 3
NA


Group 2

Person
Balance
Person 1
NA
Person 2
40
Person 3
-40

Expectations and guidelines
You are allowed to access the internet.
You are free to use any language of your choice.
Do not use any external libraries. All of the code should be your own.
Implement the code using only in memory data structures or basic file handling. Use of databases is not allowed.
Create the sample data yourself. You can put it into a file, test cases or the main driver program itself.
Your code should be demo-able either through a main driver program or test cases. Code that does not run will not be evaluated.
Code should be modular and have the correct abstractions. 
Either use Object Oriented design or functional programming. 
Do not write monolithic code.
Code should be legible, readable and DRY.
Code should be extensible. Wherever applicable, use interfaces and contracts between different methods. It should be easy to add/remove functionality without re-writing the entire codebase.
Code should handle edge cases properly and fail gracefully. Add suitable exception handling, wherever applicable.
Code should handle concurrent modification of the data.
Please focus on the Bonus questions only after ensuring the required features are complete and demoable. The bonus portion would not be evaluated if any of the required functionality is missing.
Save your code/project by your name and email it. Your program will be executed on another machine. So, explicitly specify dependencies, if any, in your email.
```