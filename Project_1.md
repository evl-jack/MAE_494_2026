# MAE 494 Fall 2026 Project one


Team Name: Ai Generated

Contributors:Jack Foster, Danny Lewis

Topic : Optimizing Student GPA by allocating hours studied

## Problem Identification

```


```

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

definitions:

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

$$= 1 - 1 * a_i$$

Constants:

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

## Classification
  











## Assumptions and Simplifications






