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
import matplotlib.pyplot as plt


# Common variables used throughout
antibiotic_list = ['Cefazolin','Ceftriaxone','Ceftazidime',
                   'Piptaz','Meropenem','Ciprofloxacin',
                   'Tobramycin','TMPSMX',
                   'Piptaz_or_Tobramycin'
                  ]

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
                      'TMPSMX':'OtherAbx'
                     }
    
regression_inputs = ['Hospital','Age','SexCat','MedVsSurgAdmission',
                     'RecentHospitalization','ICUExposure',
                     'PriorPenicillin','PriorCephalosporin','PriorCarbapenem',
                     'PriorFQ','PriorAMG','PriorOtherAbx',                     
                     'PriorCefazolinResistance', 'PriorCeftriaxoneResistance', 
                     'PriorCeftazidimeResistance', 'PriorPiptazResistance', 
                     'PriorMeropenemResistance', 'PriorCiprofloxacinResistance', 
                     'PriorTobramycinResistance', 'PriorTMPSMXResistance',
                     'ClinicalESBL'
                    ]

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
    ui.h1("Antibiotic regression models"),
    
    ui.layout_sidebar(
        
        sidebar=ui.panel_sidebar(
            ui.h3('Input'),
            
            # ui.input_select('antibiotic', 'Antibiotic', antibiotic_dict),
            # ui.input_numeric('age', 'Age:', 0, min=18, max=110),

            ui.input_radio_buttons('Hospital','Hospital:',{0:'Sunnybrook',1:'TOH'},inline=True),

            ui.h4('Demographic factors'),

            ui.input_select('Age', 'Age:', age_categories),
            ui.input_radio_buttons('SexCat','Sex:',{0:'Male',1:'Female'},inline=True),

            ui.h4('Clinical factors'),
            
            ui.input_radio_buttons('RecentHospitalization','Recent Hospitalization:',[0,1],inline=True),
            ui.input_radio_buttons('ICUExposure','ICU exposure:',[0,1],inline=True),
            ui.input_radio_buttons('MedVsSurgAdmission','Admitting service',{0:'Medical',1:'Surgical'},inline=True),
            
            ui.h4('Antimicrobial exposures'),

            ui.input_radio_buttons('PriorPenicillin','Prior penicillin:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorCephalosporin','Prior cephalosporin:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorCarbapenem','Prior carbapenem:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorFQ','Prior fluoroquinolone:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorAMG','Prior aminoglycoside:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorOtherAbx','Prior other antibiotic:',[0,1],inline=True), 

            ui.h4('Resistance history'),
            
            ui.em('Referring specifically to ',ui.strong('gram negative'),' resistance.\n'),
            
            ui.input_radio_buttons('PriorCefazolinResistance','Prior cefazolin resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorCeftriaxoneResistance','Prior ceftriaxone resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorCeftazidimeResistance','Prior ceftazidime resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorPiptazResistance','Prior piperacillin-tazobactam resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorMeropenemResistance','Prior meropenem resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorCiprofloxacinResistance','Prior ciprofloxacin resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorTobramycinResistance','Prior tobramycin resistance:',[0,1],inline=True),    
            ui.input_radio_buttons('PriorTMPSMXResistance','Prior trimethoprim-sulfamethoxazole resistance:',[0,1],inline=True),    
           
            ui.input_radio_buttons('ClinicalESBL','Clinical ESBL:',[0,1],inline=True),
        ),
        
        main=ui.panel_sidebar(
        
            ui.h3('Output'),
            ui.output_data_frame('predicted_susceptibilities'),
            # Clinical severity cutoffs: 80% if qSOFA<=2, 90% if qSOFA=3
            ui.input_radio_buttons('Severity','Clinical severity (affects 80 vs 90% cutoff):',{80:'qSOFA<=2',90:'qSOFA=3'},inline=True),
            ui.output_plot('plot'),
            ui.output_text_verbatim('output'),
            
        ),        
    ),
    
    ui.br('')
)

# Server input

def server(input, output, session):
 
    @output
    @render.data_frame

    def predicted_susceptibilities():
        
        susceptibility_outputs = []
        
        for antibiotic in antibiotic_list:
            
            with open(antibiotic+'.pickle','rb') as f:
                reg = pickle.load(f)
                    
            regression_values = [input.Hospital(),
                                 input.Age(),
                                 input.SexCat(),
                                 input.MedVsSurgAdmission(),
                                 input.RecentHospitalization(),
                                 input.ICUExposure(),
                                 
                                 input.PriorPenicillin(),
                                 input.PriorCephalosporin(),
                                 input.PriorCarbapenem(),
                                 input.PriorFQ(),
                                 input.PriorAMG(),
                                 input.PriorOtherAbx(),
                                 
                                 input.PriorCefazolinResistance(),
                                 input.PriorCeftriaxoneResistance(),
                                 input.PriorCeftazidimeResistance(),
                                 input.PriorPiptazResistance(),
                                 input.PriorMeropenemResistance(),
                                 input.PriorCiprofloxacinResistance(),
                                 input.PriorTobramycinResistance(),
                                 input.PriorTMPSMXResistance(),
                                 
                                 input.ClinicalESBL()
                                ]
            df = pd.DataFrame(columns=regression_inputs)
            df.loc[len(df)] = regression_values
                        
            susceptibility_outputs.append((antibiotic,reg.predict_proba(df)[0][0]*100))
        
        # Sort antibiotics by most to least susceptible
        susceptibility_outputs.sort(key=lambda x: x[1],reverse=True)
        
        # Convert to a pandas dataframe and add column names
        df = pd.DataFrame(susceptibility_outputs)
        df = df.rename(columns={0:'Antibiotic',1:'Predicted susceptibility (%)'})
        
        # Rename 'Piptaz_or_Tobramycin' to 'Dual piptaz + tobramycin'
        df = df.replace('Piptaz_or_Tobramycin','Dual piptaz + tobramycin')
        
        # Round numbers to 1 digits before outputting
        return(df.round(1))
    

    @output
    @render.plot
    
    def plot():
        
        susceptibility_outputs = []

        for antibiotic in antibiotic_list:
                        
            with open(antibiotic+'.pickle','rb') as f:
                reg = pickle.load(f)
                    

            regression_values = [input.Hospital(),
                                 input.Age(),
                                 input.SexCat(),
                                 input.MedVsSurgAdmission(),
                                 input.RecentHospitalization(),
                                 input.ICUExposure(),
                                 
                                 input.PriorPenicillin(),
                                 input.PriorCephalosporin(),
                                 input.PriorCarbapenem(),
                                 input.PriorFQ(),
                                 input.PriorAMG(),
                                 input.PriorOtherAbx(),
                                 
                                 input.PriorCefazolinResistance(),
                                 input.PriorCeftriaxoneResistance(),
                                 input.PriorCeftazidimeResistance(),
                                 input.PriorPiptazResistance(),
                                 input.PriorMeropenemResistance(),
                                 input.PriorCiprofloxacinResistance(),
                                 input.PriorTobramycinResistance(),
                                 input.PriorTMPSMXResistance(),
                                 
                                 input.ClinicalESBL()
                                ]
                                 
            df = pd.DataFrame(columns=regression_inputs)
            df.loc[len(df)] = regression_values
            
            prediction = reg.predict_proba(df)[0][0]
            
            # Rename 'Piptaz_or_Tobramycin' to 'Dual piptaz + tobramycin'
            if antibiotic == 'Piptaz_or_Tobramycin':
                antibiotic = 'Dual piptaz + tobramycin'
            susceptibility_outputs.append((antibiotic,prediction))
            
            # susceptibility_outputs.append((antibiotic,reg.predict_proba(df)[0][0]))
        
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
  
        # Sort antibiotics by most to least susceptible
        susceptibility_outputs.sort(key=lambda x: x[1],reverse=True)
        
        x = [i[0] for i in susceptibility_outputs]
        y = [i[1]*100 for i in susceptibility_outputs]
        
        # Plot points
        bars = ax.bar(x,y)
        ax.bar_label(bars,fmt='')        
        ax.bar_label(bars,fmt='%d')
        
        # Plot an 80% or 90% horizontal line based on clinical severity
        cutoff = int(input.Severity())
        plt.axhline(y=cutoff,color='orange',label='{}%'.format(cutoff))
        
        ax.legend()
        
        return fig
    
    
app = App(app_ui, server)

