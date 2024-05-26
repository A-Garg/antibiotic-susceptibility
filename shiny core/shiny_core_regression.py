##################################
#                                #
# shiny_core_regression.py       #
# Created 2023-05-19             #
# Akhil Garg, akhil@akhilgarg.ca #
#                                #
##################################


from shiny import App, reactive, render, ui
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

age_categories = ['<40',  '40-44','45-49','50-54','55-59', 
                  '60-64','65-69','70-74','75-79','80-84',
                  '85-89','>90'
                 ]
                 
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
        
        if input.Acquisition()=='Hospital non-ICU':
            df['acquisition_ward'] = 1
        elif input.Acquisition()=='ICU':
            df['acquisition_ICU'] = 1
        
        warnings.simplefilter(action='ignore', category=UserWarning)
        # A match-case structure may be better here
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
            
        with open(antibiotic+'_'+input.Hospital()+'.pickle','rb') as f:
            reg = pickle.load(f)
                
        susceptibility_outputs.append((antibiotic,reg.predict_proba(df)[0][0]*100))
    
    # Convert to a pandas dataframe and add column names
    df = pd.DataFrame(susceptibility_outputs)
    df = df.rename(columns={0:'Antibiotic',1:'Predicted susceptibility (%)'})

    # Rename certain antibiotics
    df = df.replace('Piptaz_or_Tobramycin','PipTazo+Tobramycin')
    df = df.replace('Piptaz','PipTazo')    
        
    return df
    
    
    
app_ui = ui.page_fluid(
    ui.h1('Gram negative resistance regression model'),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3('Input'),
            
            ui.card(
                ui.input_radio_buttons('Hospital','Hospital:',
                                      # ['Sunnybrook','TOH','Trillium'],inline=True) #replace this line when Trillium data is available
                                      ['Sunnybrook','TOH'],inline=True)
            ),
            
            ui.card(
                ui.h4('Demographic factors'),

                ui.tooltip(
                    ui.input_select('Age', 'Age:', age_categories),
                    'Age at the time of index culture collection'
                ),
                ui.tooltip(
                    ui.input_radio_buttons('SexCat','Sex:',['Male','Female'],inline=True),
                    'Sex in EMR at time of: index counter (TOH/THP) OR index culture collection (SHSC)'
                )
            ),
            
            ui.card(
                ui.h4('Clinical factors'),
                
                ui.tooltip(
                    ui.input_radio_buttons('Acquisition','Acquisition:',['Community','Hospital non-ICU','ICU'],inline=True),
                    'Community: index culture within first 48 hours of admission or whlie in ED prior to admit. ',
                    'Hospital: index culture =>48 hours after admit. '
                    'ICU: index culture =>48 hours after admit to ICU.'
                ),
                ui.tooltip(
                    ui.input_radio_buttons('RecentHospitalization','Recent Hospitalization:',{0:'No',1:'Yes'},inline=True),
                    'Hospitalization (separate) within 90 days prior to: index culture collection date (TOH/THP) OR present admission date (SHSC)'
                ),
                ui.tooltip(
                    ui.input_radio_buttons('MedVsSurgAdmission','Admitting service',['Medical','Surgical'],inline=True),
                    'Admitting hospital service for index admission'
                )
            ),
            
            ui.tooltip(
                ui.card(
                    ui.h4('Antimicrobial exposures'),
                    ui.input_radio_buttons('PriorPenicillin','Prior penicillin:',{0:'No',1:'Yes'},inline=True),    
                    ui.input_radio_buttons('PriorCephalosporin','Prior cephalosporin:',{0:'No',1:'Yes'},inline=True),    
                    ui.input_radio_buttons('PriorCarbapenem','Prior carbapenem:',{0:'No',1:'Yes'},inline=True),    
                    ui.input_radio_buttons('PriorFQ','Prior fluoroquinolone:',{0:'No',1:'Yes'},inline=True),    
                    ui.input_radio_buttons('PriorAMG','Prior aminoglycoside:',{0:'No',1:'Yes'},inline=True),    
                    ui.input_radio_buttons('PriorOtherAbx','Prior other class:',{0:'No',1:'Yes'},inline=True)
                ),
                'Antibiotic exposure in the last 90 days to 48 hours prior to the time of index culture order (SHSC) or date (TOH/THP). '
                'Only inpatient antibiotics (SHSC) OR inpatient/outpatient antibiotics in EMR (TOH/THP).'
            ),
            
            ui.tooltip(
                ui.card(
                    ui.h4('Gram negative susceptibility history'),

                    #ui.em('Referring specifically to prior ',ui.strong('gram negative'),' susceptibility.\n'),
                    
                    ui.input_radio_buttons('PriorMeropenemResistance','Prior meropenem:',prior_resistance_history,inline=True),    
                    ui.input_radio_buttons('PriorPiptazResistance','Prior piperacillin-tazobactam:',prior_resistance_history,inline=True),
                    ui.input_radio_buttons('PriorCeftazidimeResistance','Prior ceftazidime:',prior_resistance_history,inline=True),    
                    ui.input_radio_buttons('PriorCeftriaxoneResistance','Prior ceftriaxone:',prior_resistance_history,inline=True),    
                    ui.input_radio_buttons('PriorCiprofloxacinResistance','Prior ciprofloxacin:',prior_resistance_history,inline=True)
                ),
                'Most recent Gram-negative organism from clinical culture in last 72 hours to 90 days prior to culture collection date'
            ),
            
            ui.tooltip(
                ui.card(
                    ui.input_radio_buttons('ClinicalESBL','Clinical ESBL:',[0,1],inline=True),
                ),
                'Clinical (non-screening culture) for ESBL within 3 days to 12 months prior to index culture collection date',
            ),
            open='open' # Keep sidebar open by default
        ),
        
        ui.card(  
        
            ui.layout_sidebar(
            
                ui.sidebar(
                
                    # Clinical severity cutoffs: 80% if qSOFA<=2, 90% if qSOFA=3
                    ui.card(
                        ui.input_radio_buttons('Severity','Clinical severity (affects 80 vs 90% cutoff):',{80:'qSOFA<=2',90:'qSOFA=3 or vasopressor support'},inline=True),
                    ),
                    
                    ui.output_plot('plot'),
                    
                    open='open' # Keep sidebar open by default
                ),
                
                ui.output_data_frame('predicted_susceptibilities'),
                ui.output_data_frame('input_values'),

            ),
            
        ),
        
    )
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
    @render.data_frame
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
        
        df.loc  ['Prior meropenem resistance:':'Prior ciprofloxacin resistance:'] \
        = df.loc['Prior meropenem resistance:':'Prior ciprofloxacin resistance:'].replace(susceptibility_profile)
        
        # Replace remainder with Yes/No
        others = {'0':'No','1':'Yes'}
        df = df.replace(others)
        
        # Add qSOFA score to dataframe
        if int(input.Severity())==80: qSOFA='0-2'
        elif int(input.Severity())==90: qSOFA='3 or vasopressors'
        df.loc['qSOFA:'] = qSOFA
        
        # Convert DataFrame index into a column
        df['Input'] = df.index
                
        return(df[['Input','Value']])

 
app = App(app_ui, server)

