# antibiotic-susceptibility
Creating a model of antimicrobial susceptibility based on local risk factors

## Files

### iPython notebooks
* `imputation.ipynb`: Uses imputation rules to fill in antimicrobial susceptibility patterns (e.g. methicillin-susceptible *S. aureus* should also be susceptible to piperacillin-tazobactam).
* `regression.ipynb`: Creates logistic regression models for antibiotic susceptibility, and saves them in [pickle](https://docs.python.org/3/library/pickle.html) files.

### Shiny Folders
* `shiny_regression.py`: Creates an interactive visual interface for the regression model
* `shiny_core_regression.py`: An updated version that takes advantage of new Shiny features

## Example output

### Regression notebook
```
Regression model for Cefazolin
Logistic Regression Coefficients

PriorGNinf                                  1.4891
ClinicalESBL                                1.0489
PriorCephalosporin                          0.5478
ICUExposure                                 0.3666
Medical(1) Surgical (2) Admitting Service   0.3334
ClincalMRSA                                 0.1141
PriorNonCephalosporin                       0.1135
ClinicalVRE                                 0.0000
Age                                        -0.0571
RecentHospitalization                      -0.1632
SexCat                                     -0.4171`
```
![Ceftriaxone Output](https://user-images.githubusercontent.com/31163077/182207506-6cba5e0c-4dfa-40fc-bd01-fb316e8af6a1.png)

### Shiny implementation
Reactive and most recent version at: https://akhilgarg.shinyapps.io/model/

![image](https://github.com/A-Garg/antibiotic-susceptibility/assets/31163077/b02a7519-8e3d-4c82-93d5-aac742101e46)

