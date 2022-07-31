# antibiotic-susceptibility
Creating a model of antimicrobial susceptibility based on local risk factors

## Files

### iPython Notebooks
* `antimicrobial_imputation.ipynb`: Uses imputation rules to fill in antimicrobial susceptibility patterns (e.g. methicillin-susceptible *S. aureus* should also be susceptible to piperacillin-tazobactam).
* `missingness.ipynb`: Calculates the amount of missing susceptibility data for each antibiotic
* `regression.ipynb`: The actual logistic regression model for antibiotic susceptibility

### Other Files
* `AMR_imputation_6.xlsx`: Source data
