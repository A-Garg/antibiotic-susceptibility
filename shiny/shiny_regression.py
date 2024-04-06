##################################
#                                #
# shiny_regression.py            #
# Created 2023-03-11             #
# Akhil Garg, akhil@akhilgarg.ca #
#                                #
##################################


from shiny import App, render, ui
import pickle
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Common variables used throughout
antibiotic_list = ['Meropenem','Piptaz',
                   'Ceftazidime','Ceftriaxone',
                   'Ciprofloxacin','TMPSMX','Cefazolin','Piptaz_or_Tobramycin']

# New antibiotic list as of 2024-03-26
antibiotic_list = ['Meropenem','Piptaz','Ceftazidime','Ceftriaxone','Ciprofloxacin']

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
                      'TMPSMX':'OtherAbx','Piptaz_or_Tobramycin':'Penicillin_or_AMG'
                     }

# age_categories = {
                  # 1: '<40', 
                  # 2: '40-44',
                  # 3: '45-49',
                  # 4: '50-54',
                  # 5: '55-59',
                  # 6: '60-64',
                  # 7: '65-69',
                  # 8: '70-74',
                  # 9: '75-79',
                  # 10:'80-84',
                  # 11:'85-89',
                  # 12:'>90'
                 # }
                 
age_categories = ['<40',  '40-44','45-49','50-54','55-59', 
                  '60-64','65-69','70-74','75-79','80-84',
                  '85-89','>90'
                 ]

# with open('age_scaler.pickle','rb') as f: age_StandardScaler = pickle.load(f)
                 
prior_resistance_history = {0:'No isolate or unknown',1:'Susceptible',2:'Nonsusceptible'}  


def susceptibility_outputs_f(input):
    '''
    Function that takes in shiny input values and a particular antibiotic
        (or combination piperacillin-tazobactam and tobramycin)
    Returns a Pandas DataFrame containing susceptibility outputs
    '''
    susceptibility_outputs = []

    for antibiotic in antibiotic_list:

        # Create a DataFrame of regression inputs that are all zeros
        regression_inputs = ['Age','sex_M',
                             
                             'acquisition_ICU','acquisition_ward',
                             'adm_service_surgical','RecentHospitalization',
                             
                             'Prior'+antibiotic_classes[antibiotic],
                             'PriorNon'+antibiotic_classes[antibiotic],
                              antibiotic+'Resistance_susceptible',antibiotic+'Resistance_nonsusceptible',
                             
                             'ClinicalESBL']        
                             
        df = pd.DataFrame(np.zeros(shape=(1,len(regression_inputs))),columns=regression_inputs)

        # Start populating the DataFrame
        
        # if input.Hospital()==   'Sunnybrook': df['hosp_Sunnybrook'] = 1
        # elif input.Hospital()== 'TOH':        df['hosp_TOH'] = 1
        
        if input.Acquisition()=='Hospital non-ICU':
            df['acquisition_ward'] = 1
        elif input.Acquisition()=='ICU':
            df['acquisition_ICU'] = 1
        
        warnings.simplefilter(action='ignore', category=UserWarning)
        # A match-case structure may be better here
        
        # # Scaled version of age
        # if   input.Age()=='<40'  : df['age_scaled'] = age_StandardScaler.transform([[30]])
        # elif input.Age()=='40-44': df['age_scaled'] = age_StandardScaler.transform([[42.5]])
        # elif input.Age()=='45-49': df['age_scaled'] = age_StandardScaler.transform([[47.5]])
        # elif input.Age()=='50-54': df['age_scaled'] = age_StandardScaler.transform([[52.5]])
        # elif input.Age()=='55-59': df['age_scaled'] = age_StandardScaler.transform([[57.5]])
        # elif input.Age()=='60-64': df['age_scaled'] = age_StandardScaler.transform([[62.5]])
        # elif input.Age()=='65-69': df['age_scaled'] = age_StandardScaler.transform([[67.5]])
        # elif input.Age()=='70-74': df['age_scaled'] = age_StandardScaler.transform([[72.5]])
        # elif input.Age()=='75-79': df['age_scaled'] = age_StandardScaler.transform([[77.5]])
        # elif input.Age()=='80-84': df['age_scaled'] = age_StandardScaler.transform([[82.5]])
        # elif input.Age()=='85-89': df['age_scaled'] = age_StandardScaler.transform([[87.5]])
        # elif input.Age()=='>90'  : df['age_scaled'] = age_StandardScaler.transform([[95]])

        # # Unscaled version of age
        if   input.Age()=='<40'  : df['Age'] = 30
        elif input.Age()=='40-44': df['Age'] = 42.5
        elif input.Age()=='45-49': df['Age'] = 47.5
        elif input.Age()=='50-54': df['Age'] = 52.5
        elif input.Age()=='55-59': df['Age'] = 57.5
        elif input.Age()=='60-64': df['Age'] = 62.5
        elif input.Age()=='65-69': df['Age'] = 67.5
        elif input.Age()=='70-74': df['Age'] = 72.5
        elif input.Age()=='75-79': df['Age'] = 77.5
        elif input.Age()=='80-84': df['Age'] = 82.5
        elif input.Age()=='85-89': df['Age'] = 87.5
        elif input.Age()=='>90'  : df['Age'] = 95
        
        if input.SexCat()=='Male': df['sex_M'] = 1
        if input.MedVsSurgAdmission()=='Surgical': df['adm_service_surgical'] = 1
        
        df['RecentHospitalization'] = input.RecentHospitalization()
        df['ClinicalESBL']          = input.ClinicalESBL()
        
                             
        # Handling prior exposure and resistance history
        
        # Special handling for combined piperacillin-tazobactam and tobramycin
        if antibiotic=='Piptaz_or_Tobramycin':
        
            # Prior class exposure
            if int(input.PriorPenicillin())==1 or int(input.PriorAMG())==1:
                df['PriorPenicillin_or_AMG'] = 1
            else: df['PriorPenicillin_or_AMG'] = 0
            
            # Prior non-class exposure
            if (int(input.PriorCephalosporin())==1 
             or int(input.PriorCarbapenem())==1
             or int(input.PriorFQ())==1
             or int(input.PriorAMG())==1
             or int(input.PriorOtherAbx())==1):
                df['PriorNonPenicillin_or_AMG'] = 1
            else: df['PriorNonPenicillin_or_AMG'] = 0
            
            # Prior resistance
            if   (int(input.PriorPiptazResistance())==0 and int(input.PriorTobramycinResistance())==0):
                pass
            elif (int(input.PriorPiptazResistance())==0 or  int(input.PriorTobramycinResistance())==0):
                df['Piptaz_or_TobramycinResistance_susceptible'] = 1
            elif (int(input.PriorPiptazResistance())==1 or  int(input.PriorTobramycinResistance())==1):
                df['Piptaz_or_TobramycinResistance_susceptible'] = 1                
            elif (int(input.PriorPiptazResistance())==2 and int(input.PriorTobramycinResistance())==2):
                df['Piptaz_or_TobramycinResistance_nonsusceptible'] = 1
                
            else: raise ValueError('Something went wrong with combined pip-tazo/tobra susceptibility')
            
        # Handling all other antibiotics
        else:
            
            # Prior class exposure
            df['Prior'+antibiotic_classes[antibiotic]] = int(input['Prior'+antibiotic_classes[antibiotic]]())
            
            
            # Prior non-class exposure
            # Remove the antibiotic class from the set of antibiotic classes to check
            prior_nonclasses = set(i for i in antibiotic_classes.values() if i!=antibiotic_classes[antibiotic])
            
            # Remove Penicillin_or_AMG from the set of antibiotic classes as we do not have input for it
            # (it was handled separately)
            prior_nonclasses.remove('Penicillin_or_AMG')
           
            # If any of the prior exposures in the set is 1, the resulting value is 1
            # Sum the number of non-class antibiotic exposures
            i = 0
            for abx_class in prior_nonclasses: 
                 i+=int(input['Prior'+abx_class]())
            if   i==0: df['PriorNon'+antibiotic_classes[antibiotic]] = 0
            elif i>=1: df['PriorNon'+antibiotic_classes[antibiotic]] = 1
            else: raise ValueError('The number of prior non class exposures is not zero or a positive integer')
            
            
            # Prior antibiotic resistance
            if int(input['Prior'+antibiotic+'Resistance']())==1:
                df[antibiotic+'Resistance_susceptible'] = 1
            elif int(input['Prior'+antibiotic+'Resistance']())==2:
                df[antibiotic+'Resistance_nonsusceptible'] = 1
            
        with open(antibiotic+'.pickle','rb') as f:
            reg = pickle.load(f)
                
        susceptibility_outputs.append((antibiotic,reg.predict_proba(df)[0][0]*100))
    
    # Convert to a pandas dataframe and add column names
    df = pd.DataFrame(susceptibility_outputs)
    df = df.rename(columns={0:'Antibiotic',1:'Predicted susceptibility (%)'})

    # Rename certain antibiotics
    df = df.replace('Piptaz_or_Tobramycin','Pip/Tazo+Tobramycin')
    df = df.replace('Piptaz','Pip/Tazo')    
        
    return df
                 
app_ui = ui.page_fluid(
    ui.h1("Gram negative resistance regression model"),
    
    ui.layout_sidebar(
        
        sidebar=ui.panel_sidebar(
            ui.h3('Input'),
            
            # ui.input_select('antibiotic', 'Antibiotic', antibiotic_dict),

            ui.input_radio_buttons('Hospital','Hospital: currently pending data from TOH and Trillium, so will not affect output',
                ['Sunnybrook','TOH','Trillium'],inline=True),

            ui.h4('Demographic factors'),

            ui.input_select('Age', 'Age:', age_categories),
            ui.input_radio_buttons('SexCat','Sex:',['Male','Female'],inline=True),

            ui.h4('Clinical factors'),
            
            ui.input_radio_buttons('Acquisition','Acquisition:',['Community','Hospital non-ICU','ICU'],inline=True),
            ui.input_radio_buttons('RecentHospitalization','Recent Hospitalization:',{0:'No',1:'Yes'},inline=True),
            ui.input_radio_buttons('MedVsSurgAdmission','Admitting service',['Medical','Surgical'],inline=True),
            
            ui.h4('Antimicrobial exposures'),

            ui.input_radio_buttons('PriorPenicillin','Prior penicillin:',{0:'No',1:'Yes'},inline=True),    
            ui.input_radio_buttons('PriorCephalosporin','Prior cephalosporin:',{0:'No',1:'Yes'},inline=True),    
            ui.input_radio_buttons('PriorCarbapenem','Prior carbapenem:',{0:'No',1:'Yes'},inline=True),    
            ui.input_radio_buttons('PriorFQ','Prior fluoroquinolone:',{0:'No',1:'Yes'},inline=True),    
            ui.input_radio_buttons('PriorAMG','Prior aminoglycoside:',{0:'No',1:'Yes'},inline=True),    
            ui.input_radio_buttons('PriorOtherAbx','Prior other class:',{0:'No',1:'Yes'},inline=True), 

            ui.h4('Susceptibility history'),
            
            ui.em('Referring specifically to prior ',ui.strong('gram negative'),' susceptibility.\n'),
            
            # ui.input_radio_buttons('PriorCefazolinResistance','Prior cefazolin:',prior_resistance_history,inline=True),    
            ui.input_radio_buttons('PriorMeropenemResistance','Prior meropenem:',prior_resistance_history,inline=True),    
            ui.input_radio_buttons('PriorPiptazResistance','Prior piperacillin-tazobactam:',prior_resistance_history,inline=True),
            ui.input_radio_buttons('PriorCeftazidimeResistance','Prior ceftazidime:',prior_resistance_history,inline=True),    
            ui.input_radio_buttons('PriorCeftriaxoneResistance','Prior ceftriaxone:',prior_resistance_history,inline=True),    
            ui.input_radio_buttons('PriorCiprofloxacinResistance','Prior ciprofloxacin:',prior_resistance_history,inline=True),    
            # ui.input_radio_buttons('PriorTobramycinResistance','Prior tobramycin:',prior_resistance_history,inline=True),    
            # ui.input_radio_buttons('PriorTMPSMXResistance','Prior trimethoprim-sulfamethoxazole:',prior_resistance_history,inline=True),    
           
            ui.input_radio_buttons('ClinicalESBL','Clinical ESBL:',[0,1],inline=True),
        ),
        
        main=ui.panel_sidebar(

            ui.h3('Output'),
            ui.output_data_frame('predicted_susceptibilities'),
            
            # Clinical severity cutoffs: 80% if qSOFA<=2, 90% if qSOFA=3
            ui.input_radio_buttons('Severity','Clinical severity (affects 80 vs 90% cutoff):',{80:'qSOFA<=2',90:'qSOFA=3 or vasopressor support'},inline=True),
            ui.output_plot('plot'),
            
            ui.h3('Inputs'),
            # ui.output_data_frame('input_values'),
            ui.output_text_verbatim('input_values'),
                        
        ),        
    ),
    
    ui.br('')
)


def server(input, output, session):
  
    @output
    @render.data_frame

    def predicted_susceptibilities():
        
        df = susceptibility_outputs_f(input)
        
        # Add colons after each antibiotic
        df['Antibiotic'] = df['Antibiotic'] + ':'
       
        # Round numbers to n digits before outputting
        return(df.round(0))
    
    @output
    @render.plot
    
    def plot():
        
        df = susceptibility_outputs_f(input)

        # Create a plot       
        fig, ax = plt.subplots()
        ax.clear()
        
        # Format the plot
        ax.set_xlabel('Antibiotic')
        ax.set_ylabel('Susceptibility (%)')
        ax.set_ylim(0,100)
        ax.tick_params('x',rotation = 80)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # x = [i[0] for i in susceptibility_outputs]
        # y = [i[1]*100 for i in susceptibility_outputs]
        x = df['Antibiotic']
        y = df['Predicted susceptibility (%)']
        
        # Plot points
        bars = ax.bar(x,y)
        ax.bar_label(bars,fmt='')        
        ax.bar_label(bars,fmt='%d')
        
        # Plot an 80% or 90% horizontal line based on clinical severity
        cutoff = int(input.Severity())
        plt.axhline(y=cutoff,color='orange',label='{}%'.format(cutoff))
        
        ax.legend()
        
        return fig

    
    # Code to display input values
    @output
    @render.text
    def input_values():
        
        df = pd.DataFrame(data=[input.Hospital(),
                                input.Age(),
                                input.SexCat(),
                                input.Acquisition(),
                                input.MedVsSurgAdmission(),
                                input.RecentHospitalization(),
                                input.ClinicalESBL(),

                                input.PriorPenicillin(),
                                input.PriorCephalosporin(),
                                input.PriorCarbapenem(),
                                input.PriorFQ(),
                                input.PriorAMG(),
                                input.PriorOtherAbx(),
                             
                                input.PriorMeropenemResistance(),
                                input.PriorPiptazResistance(),
                                input.PriorCeftazidimeResistance(),                                
                                input.PriorCeftriaxoneResistance(),
                                input.PriorCiprofloxacinResistance(),
                            
                               ],
                               
                          index=['Hospital:',
                                 'Age:',
                                 'Sex:',
                                 'Acquisition:',
                                 'Admitting service:',
                                 'Recent hospitalization:',
                                 'Clinical ESBL:',
                                 
                                 'Prior penicillin:',
                                 'Prior cephalosporin:',
                                 'Prior carbapenem:',
                                 'Prior fluoroquinolone:',
                                 'Prior aminoglycoside:',
                                 'Prior other class:',

                                 'Prior meropenem resistance:',
                                 'Prior piperacillin-tazobactam resistance:',
                                 'Prior ceftazidime resistance:',
                                 'Prior ceftriaxone resistance:',
                                 'Prior ciprofloxacin resistance:'
                                ])
                                
        df = df.rename(columns={0:'Value'})      

        # Replace resistance questions with susceptible/unknown/missing or nonsusceptible
        susceptibility_profile = {'0':'No previous/Unknown','1':'Susceptible','2':'Nonsusceptible'}
        #df.loc  ['Prior cefazolin resistance:':'Prior trimethoprim-sulfamethoxazole resistance:'] \
        #= df.loc['Prior cefazolin resistance:':'Prior trimethoprim-sulfamethoxazole resistance:'].replace(susceptibility_profile)
        
        # On 2024-03-26, cefazolin, TMPSMX, and combined piperacillin-tazobactam and tobramycin were removed
        # Thus leading to a smaller DataFrame
        df.loc  ['Prior meropenem resistance:':'Prior ciprofloxacin resistance:'] \
        = df.loc['Prior meropenem resistance:':'Prior ciprofloxacin resistance:'].replace(susceptibility_profile)
        
        # Replace remainder with Yes/No
        others = {'0':'No','1':'Yes'}
        df = df.replace(others)
        
        # Add qSOFA score to dataframe
        if int(input.Severity())==80: qSOFA='0-2'
        elif int(input.Severity())==90: qSOFA='3 or vasopressors'
        df.loc['qSOFA:'] = qSOFA
        
        
        return(df)
        
        
app = App(app_ui, server)

