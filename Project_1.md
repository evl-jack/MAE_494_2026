# MAE 494 Fall 2026 Project one


Team Name: Ai Generated

Contributors:Jack Foster, Danny Lewis

Topic : Optimizing Student GPA by allocating hours studied

## Problem Identification

Most college students are very busy and many have to get a job or take on other resposibilities. It can be hard for most students to be able to plan how much studying they really need to do especially when they have other things to plan such as work avalibility or extra cirriculars. In order to make these decisions it would require the student to sit down and spend quite a while planning their weeks. 

It is very important that students develope time management skills, and sometimes that hardest part is building a good study schedule that works withs with the students other time constraints. 

This Algorith takes the students outside activities such as sleep and work and distributes the remaining time to studying. The algorith will divide the students remaining time based on the amount of credit hours and difficulty of the class. Being able to figure out how much time you should realisticaly be spending studying certin subjects is hard and will have negative consequeses on their grades.


## Decision Variables
 Variable $x_i$ representing the # hours a student spent studying subject $i$
 
$$x_i \epsilon ℝ$$  

$$x_i \ge 0$$
```

```

## Objective Function

The objective is to maximize GPA. GPA is defined as $(Grade Points Earned * Credit Hours) / (Credit Hours)$ to fully define this function.

$$G \epsilon ℝ$$  $0 \le G \le 4.0$  : GPA  standard U.S grading scale

$C_i$ : total credit hours taken in a students block 

$$P(x_i)$$ : Grade point earned per class $i$

$$\max G = \max_P \frac{\Sigma(P(x_i) * C_i)}{\Sigma C_i}$$ 
```
```

## More Definitions
This algorithum requires more definitions to fully define

**definitions:**

- **Grade point earned in class** : function of $x_i$ amount of hours spent studying for class $i$

$$P_i(x_i) \epsilon ℝ  \le 4$$

$$\le b_i + x_i * a_i$$

- **Difficulty**: arbitary constant used to assign a value to the students confidence in each individual class
>Please see [Assumptions and Simplifications](#Assumptions-and-Simplifications) for better explination to the interpritation of this constant 

$$d_i \epsilon ℝ$$  $$0 < d_i \le 10$$

- **Grade point earned per hour**: rate of change of grade point average earned relative to the # of hours studied
>Please see [Assumptions and Simplifications](#Assumptions-and-Simplifications) for better explination to the interpritation

$$a_i \epsilon ℝ$$ 

$$= \frac{2}{d_i + m_i - m_i}  $$

- **Base grade point**: base grade point value assigned to each students class relative to $a_i$
>Please see [Assumptions and Simplifications](#Assumptions-and-Simplifications) for better explination to the interpritation

$$b_i \epsilon  \(\mathbb{Z}\)$$

$$= 1 - m_i * a_i$$

**Constants:**

$S$ : # of hours a sleep a student needs per week

$W$ : # of hours student works per week

$D$ : # of hours student spends in class per week

$R$ : # of hours studenr require to maintain ones self

$m_i$ : minimum # of hours a student must spend on on class per week

$$m_i = C_i - 1$$

$H$ : Remaining hours a student has left in a week to study

$$H = 168 - ( S + W + D + R + m_i)$$


## Constraints

- Standard U.S grading system

$$0 \le P_i (x) \le 4$$

- Required minimum study hours per class

$$x_i  \ge m_i \ge 0$$

- Maximum study hours per week

 $$\Sigma x_i \le H$$

-Minimum Grade Required to pass a class

 $$P_i \ge 2$$
## Classification

This problem is classified as a linear programming problem. the main constraint eqaution $P_i(x_i)$ is able to be represented as a linear inequality.

$$P_i(x_i) \le b_i + x_i * a_i$$

If we graphed this linear system of eqautions assuming there are $i$ amount of classes then $i$ linear lines will apear on the graph stoping within in the bounds of the constraints. The solution vector $\vec{x}$ will equal some point on these lines where $x_i$ is bound to there individual function $P_i(x_i)$. This can be defined as a convex set as each point will be found in there respective domain.
  


## Assumptions and Simplifications

- We assume $d_i$ to be a good estimation from student

$$0 < d_i \le 10$$

- Assuming that if a student studies the minimum amount of hours $m_i$ then they will receive a grade of a D
  
$$x_i = m_i \top p_i(x_i) = 1$$

- $d_i + m_i$ is the amount of time a student needs to achive a $B$

$$x_i = d_i + m_i \top P_i(x_i) = 3$$

- each additional hour studied impoves the students grade linearly until it reach the upper bound $4.0$

Making these assumptions and simplifications makes this algorithum a good approximation based on how difficult a student interprets the class to be. To gain a good solution real emperical data should be collected pertaining to each specific class comparing the grades of students who studied for $x_i$ amount of hours. After gathering this data the algorithum would have to ask for specific class codes and be able to serch a liabary of these values. I also would expect this data to be far from linear for most classes.

This formula leaves alot of descion to the user asking them to make close approximations to how they usally allocate their time on a weekly basis. Idealy I would want to take this descion from the away from the user and add nessisary constraint equations to optimize every aspect of the students week.














