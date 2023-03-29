from shiny import App, render, ui
import pickle
import pandas as pd

antibiotic_list = ['Piptaz_or_Tobramycin']

antibiotic_dict = {'Combinations':{'Piptaz_or_Tobramycin':'Piperacillin-tazobactam and tobramycin'}}

regression_inputs = ['Age','SexCat','MedVsSurgAdmission','ClinicalESBL',
                     'RecentHospitalization','ICUExposure',
                     'PriorGNresistance','PriorPenicillin','PriorAMG','PriorNonPenicillin','PriorNonAMG']

age_categories = {
1: '<40', 
2: '40-44',
3: '45-49',
4: '50-54',
5: '55-59',
6: '60-64',
7: '65-69',
8: '70-74',
9: '75-79',
10:'80-84',
11:'85-89',
12:'>90'}  

app_ui = ui.page_fluid(
    ui.h2("Antimicrobial regression models"),
    ui.input_select('antibiotic', 'Antibiotic', antibiotic_dict),
    # ui.input_numeric('age', 'Age:', 0, min=18, max=110),
    ui.input_select('Age', 'Age:', age_categories),

    ui.input_radio_buttons('SexCat','Sex:',{0:'Male',1:'Female'},inline=True),
    ui.input_radio_buttons('ClinicalESBL','Clinical ESBL:',[0,1],inline=True),
    ui.input_radio_buttons('RecentHospitalization','Recent Hospitalization:',[0,1],inline=True),
    ui.input_radio_buttons('ICUExposure','ICU exposure:',[0,1],inline=True),
    ui.input_radio_buttons('PriorGNresistance','Prior gram negative resistance:',[0,1],inline=True),
    ui.input_radio_buttons('PriorPenicillin','Prior penicillin exposure:',[0,1],inline=True),
    ui.input_radio_buttons('PriorAMG','Prior aminoglycoside exposure:',[0,1],inline=True),
    ui.input_radio_buttons('PriorNonPenicillin','Prior non-penicillin antibiotic exposure:',[0,1],inline=True),
    ui.input_radio_buttons('PriorNonAMG','Prior non-aminoglycoside antibiotic exposure:',[0,1],inline=True),
    ui.input_radio_buttons('MedVsSurgAdmission','Admission type',{0:'Medical',1:'Surgical'},inline=True),
    
    ui.output_text_verbatim('output')
)


def server(input, output, session):
    @output
    @render.text
    
    def output():
        '''Main output'''
        
        with open('../pickle_files/'+input.antibiotic()+'.pickle','rb') as f:
            reg = pickle.load(f)
                

        regression_values = [input.Age(),
                             input.SexCat(),
                             input.MedVsSurgAdmission(),
                             input.ClinicalESBL(),
                             input.RecentHospitalization(),
                             input.ICUExposure(),
                             input.PriorGNresistance(),
                             input.PriorPenicillin(),
                             input.PriorAMG(),
                             input.PriorNonPenicillin(),
                             input.PriorNonAMG()
                            ]
                             
        df = pd.DataFrame(columns=regression_inputs)
        df.loc[len(df)] = regression_values
        
        susceptibility = reg.predict_proba(df)[0][0]

        return ('''Antibiotic:                    {} 
Probability of susceptibility: {:.1f}%'''.format(input.antibiotic(),susceptibility*100))

app = App(app_ui, server)
