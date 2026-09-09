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









