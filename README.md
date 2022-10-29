# antibiotic-susceptibility
Creating a model of antimicrobial susceptibility based on local risk factors

## Files

### iPython Notebooks
* `antimicrobial_imputation.ipynb`: Uses imputation rules to fill in antimicrobial susceptibility patterns (e.g. methicillin-susceptible *S. aureus* should also be susceptible to piperacillin-tazobactam).
* `missingness.ipynb`: Calculates the amount of missing susceptibility data for each antibiotic
* `regression.ipynb`: The actual logistic regression model for antibiotic susceptibility

### Other Files
* `AMR_imputation_6.xlsx`: Source data

## Example output

```
Regression model for Cefazolin

Logistic Regression Coefficients
PriorGNresistance                           1.4911
ClinicalESBL                                1.0636
PriorCephalosporin                          0.5474
ICUExposure                                 0.3696
MedVsSurgAdmission                          0.3324
PriorNonCephalosporin                       0.1171
Age                                        -0.0567
RecentHospitalization                      -0.1624
SexCat                                     -0.4152

Probability of susceptibility: prediction outputs
Susceptible isolates min:     0.07
                     median:  0.68
                     mean:    0.65
                     max:     0.80
                     
Resistant isolates   min:     0.04
                     median:  0.51
                     mean:    0.47
                     max:     0.79
                     

Bin minimum   S count  R count  S percentage
       0.00         1       18          0.05
       0.10         1       32          0.03
       0.20         5       24          0.17
       0.30        19       32          0.37
       0.40        14       33          0.30
       0.50        42       43          0.49
       0.60       102       61          0.63
       0.70       121       45          0.73
       0.80         3        0          1.00
       0.90         0        0           nan
```
![Cefazolin output](https://user-images.githubusercontent.com/31163077/198854338-c4f57208-880c-4b2d-ab50-9af27394b30d.png)
