# MAE 494 Fall 2026 — Project 1

Team Name: AI Generated

Contributors: Jack Foster, Danny Lewis

Topic: Optimizing Student GPA by Allocating Study Hours

## Problem Identification

Many college students balance coursework with jobs and other responsibilities. Planning how much time to spend studying can be difficult when students must also account for work availability and extracurricular activities. Creating a weekly schedule that accommodates these commitments can take considerable time.

Developing time management skills is important, but one of the hardest parts is building a study schedule that fits a student's other time constraints.

This algorithm accounts for commitments such as sleep and work, then allocates the remaining time to studying. It distributes study time among classes based on their credit hours and difficulty. The goal is to help students estimate how much time to spend on each subject and avoid study schedules that could negatively affect their grades.

## Decision Variables

The variable $x_i$ represents the number of hours a student spends studying subject $i$ per week.

$$x_i \in \mathbb{R}$$

$$x_i \ge 0$$

## Objective Function

The objective is to maximize GPA, calculated by dividing the sum of each class's grade points multiplied by its credit hours by the total credit hours.

- $G$: GPA on the standard U.S. 4.0 scale, where $G \in \mathbb{R}$ and $0 \le G \le 4.0$.
- $C_i$: Credit hours for class $i$.
- $P_i(x_i)$: Grade points earned in class $i$ as a function of weekly study hours.

$$\max G = \max_P \frac{\sum_i P_i(x_i) C_i}{\sum_i C_i}$$

## Additional Definitions

The following definitions describe how study hours relate to grade points.

- **Grade points earned in a class:** A function of the number of hours $x_i$ spent studying for class $i$, subject to the following upper bounds:

$$P_i(x_i) \in \mathbb{R}, \qquad P_i(x_i) \le 4$$

$$P_i(x_i) \le b_i + x_i a_i$$

- **Difficulty:** A constant representing the student's assessment of the difficulty of each class. See [Assumptions and Simplifications](#assumptions-and-simplifications) for its interpretation in this model.

$$d_i \in \mathbb{R}, \qquad 0 < d_i \le 10$$

- **Grade points earned per study hour:** The rate at which grade points in class $i$ increase with each additional hour of weekly study. See [Assumptions and Simplifications](#assumptions-and-simplifications) for the assumptions behind this rate.

$$a_i \in \mathbb{R}$$

$$a_i = \frac{2}{d_i + m_i - m_i}$$

- **Base grade point value:** The intercept of the linear grade model for class $i$, calculated using $m_i$ and $a_i$. See [Assumptions and Simplifications](#assumptions-and-simplifications) for the assumptions behind this value.

$$b_i \in \mathbb{R}$$

$$b_i = 1 - m_i a_i$$

### Constants

- $S$: Hours of sleep a student needs per week.
- $W$: Hours a student works per week.
- $D$: Hours a student spends attending classes per week.
- $R$: Hours a student needs for personal care per week.
- $m_i$: Minimum hours a student must spend studying for class $i$ per week.

$$m_i = C_i - 1$$

- $H$: Total hours available for studying each week after sleep, work, class attendance, and personal care.

$$H = 168 - (S + W + D + R)$$

Each $x_i$ includes the minimum study hours $m_i$ for that class. These minimums are enforced by $x_i \ge m_i$ and are not subtracted from $H$, which would count them twice.

## Constraints

- **Grade point bounds:** Grade points must fall within the standard U.S. 4.0 scale.

$$0 \le P_i(x_i) \le 4$$

- **Minimum study hours:** Each class requires a minimum amount of weekly study time.

$$x_i \ge m_i \ge 0$$

- **Maximum study hours:** Total weekly study time cannot exceed the available hours.

$$\sum_i x_i \le H$$

- **Minimum passing grade:** This model requires at least 2.0 grade points in each class.

$$P_i(x_i) \ge 2$$

## Classification

This problem is formulated as a linear programming problem. With the credit hours and model parameters fixed, the GPA objective is linear in the grade point variables. The relationship between study hours and grade points can be represented by a linear inequality:

$$P_i(x_i) \le b_i + x_i a_i$$

For each class, this inequality bounds the grade points achievable for a given number of study hours. Together with the remaining linear constraints, these inequalities define a convex feasible region. The solution specifies a study-hour allocation $\vec{x}$ and corresponding grade point values that maximize GPA within this region.

## Assumptions and Simplifications

- The student's estimate of class difficulty, $d_i$, is assumed to be reasonable.

$$0 < d_i \le 10$$

- Studying for the minimum number of hours, $m_i$, is assumed to produce a D, equivalent to 1.0 grade point.

$$x_i = m_i \implies P_i(x_i) = 1$$

- Studying for $d_i + m_i$ hours is assumed to produce a B, equivalent to 3.0 grade points.

$$x_i = d_i + m_i \implies P_i(x_i) = 3$$

- Each additional hour of weekly study is assumed to improve the student's grade linearly until it reaches the upper bound of 4.0.

These assumptions allow the algorithm to estimate grades based on a student's perception of each class's difficulty. To improve the model, empirical data should be collected for individual classes to compare study hours with grades earned. The algorithm could then ask for class codes and look up the corresponding values in a database. In practice, the relationship between study time and grades may be nonlinear for many classes.

The current model relies on the user's estimates of how they allocate their time each week. A future version could reduce this reliance by adding constraints that account for more of the student's weekly activities and help optimize the overall schedule.
