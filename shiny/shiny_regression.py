##################################
#                                #
# shiny_regression.py            #
# Created 2023-03-11             #
# Akhil Garg, akhil@akhilgarg.ca #
#                                #
##################################


from shiny import App, render, ui
import pickle
import pandas as pd

antibiotic_list = ['Cefazolin','Ceftriaxone','Ceftazidime','Piptaz','Meropenem','Ciprofloxacin','Tobramycin','TMPSMX']

antibiotic_dict = {'Pencillins':     {'Piptaz':'Piperacillin-tazobactam'},
                   'Cephalosporins': {'Cefazolin':'Cefazolin','Ceftriaxone':'Ceftriaxone','Ceftazidime':'Ceftazidime'},
                   'Carbapenems':    {'Meropenem':'Meropenem'},
                   'Quinolones':     {'Ciprofloxacin':'Ciprofloxacin'},
                   'Aminoglycosides':{'Tobramycin':'Tobramycin'},
                   'Other':          {'TMPSMX':'Trimethoprim-sulfamethoxazole'},
                   'Combinations':   {'Piptaz_or_Tobramycin':'Piperacillin-tazobactam and tobramycin'}
                  }

antibiotic_classes = {'Cefazolin':'Cephalosporin','Ceftriaxone':'Cephalosporin','Ceftazidime':'Cephalosporin',
                      'Piptaz':'Penicillin','Meropenem':'Carbapenem','Ciprofloxacin':'FQ','Tobramycin':'AMG',
                      'TMPSMX':'OtherAbx'}
    
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
    ui.h1("Antimicrobial regression models"),
    
    ui.h2('Output'),
    ui.output_text_verbatim('output'),
    
    ui.h2('Input'),
    ui.input_select('antibiotic', 'Antibiotic', antibiotic_dict),
    # ui.input_numeric('age', 'Age:', 0, min=18, max=110),
    ui.input_select('Age', 'Age:', age_categories),

    ui.input_radio_buttons('SexCat','Sex:',{0:'Male',1:'Female'},inline=True),
    ui.input_radio_buttons('ClinicalESBL','Clinical ESBL:',[0,1],inline=True),
    ui.input_radio_buttons('RecentHospitalization','Recent Hospitalization:',[0,1],inline=True),
    ui.input_radio_buttons('ICUExposure','ICU exposure:',[0,1],inline=True),
    ui.input_radio_buttons('MedVsSurgAdmission','Admission type',{0:'Medical',1:'Surgical'},inline=True),
    
    # Single antibiotic choices
    ui.panel_conditional("input.antibiotic != 'Piptaz_or_Tobramycin'",
    
        ui.input_radio_buttons('PriorSameClassAbx','Prior antibiotic from same class:',[0,1],inline=True),
        ui.input_radio_buttons('PriorDiffClassAbx','Prior antibiotic from different class:',[0,1],inline=True),
    ),

    # Combination antibiotic choices
    ui.panel_conditional("input.antibiotic == 'Piptaz_or_Tobramycin'",
    
        ui.input_radio_buttons('PriorPenicillin','Prior penicillin exposure:',[0,1],inline=True),
        ui.input_radio_buttons('PriorAMG','Prior aminoglycoside exposure:',[0,1],inline=True),
        ui.input_radio_buttons('PriorNonPenicillin','Prior non-penicillin antibiotic exposure:',[0,1],inline=True),
        ui.input_radio_buttons('PriorNonAMG','Prior non-aminoglycoside antibiotic exposure:',[0,1],inline=True)
    ),
    
    ui.input_radio_buttons('PriorGNresistance','Prior gram negative resistance:',[0,1],inline=True),
    ui.em('If the patient has had a previous gram negative organism isolated, pick 0 if the previous one was susceptible, or 1 if resistant or unknown. If no previous gram negative organism was isolated, pick 0.'),
    ui.br('')
)


def server(input, output, session):
    @output
    @render.text
    
    def output():
        '''Main output'''
        
        # Case of a single antibiotic
        if input.antibiotic() != 'Piptaz_or_Tobramycin':
        
            with open('../pickle_files/'+input.antibiotic()+'.pickle','rb') as f:
                reg = pickle.load(f)
                    
            regression_inputs = ['Age','SexCat','MedVsSurgAdmission','ClinicalESBL',
                                 'RecentHospitalization','ICUExposure','PriorGNresistance',
                                 'Prior'+antibiotic_classes[input.antibiotic()],
                                 'PriorNon'+antibiotic_classes[input.antibiotic()]]
            regression_values = [input.Age(),
                                 input.SexCat(),
                                 input.MedVsSurgAdmission(),
                                 input.ClinicalESBL(),
                                 input.RecentHospitalization(),
                                 input.ICUExposure(),
                                 input.PriorGNresistance(),
                                 input.PriorSameClassAbx(),
                                 input.PriorDiffClassAbx()]
                                 
            df = pd.DataFrame(columns=regression_inputs)
            df.loc[len(df)] = regression_values
            
            susceptibility = reg.predict_proba(df)[0][0]

            return ('''Antibiotic:                    {}
Probability of susceptibility: {:.1f}%'''.format(input.antibiotic(),susceptibility*100))
        
        # Case of a combination antibiotic
        else: 
            
            regression_inputs = ['Age','SexCat','MedVsSurgAdmission','ClinicalESBL',
                                 'RecentHospitalization','ICUExposure',
                                 'PriorGNresistance',
                                 'PriorPenicillin','PriorAMG','PriorNonPenicillin','PriorNonAMG']
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
            return ('''Antibiotics:                   {}
Probability of susceptibility: {:.1f}%'''.format(input.antibiotic(),susceptibility*100))
            print('doeo')
        
app = App(app_ui, server)
