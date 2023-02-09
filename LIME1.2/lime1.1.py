"""
Author: Bowen Yang
Date: 2023-01-08

This file contains 3 parts
1. GUI
2. Filter out all putative identities, and then sort by confidence score (determined by ppm error, RT error, adduct type, etc.)
3. Output the results, and statistical analysis on the results

"""


from re import A, S
import tkinter as tk
from turtle import clear
import pandas as pd
import numpy as np
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import math




#1. GUI
window = tk.Tk()
window.title('LIME')
window.geometry('800x700')

#1.1 Image
canvas = tk.Canvas(window, height=250, width=480)
image_file = tk.PhotoImage(file='logo.png')
image = canvas.create_image(0,0, anchor='nw', image=image_file)
canvas.pack(side='top')    #put canvas (top)


#1.2 Input file
tk.Label(window, text='Input File Name: ').place(x=100, y=270)
var_m = tk.StringVar(value = 'input.csv')
entry_m = tk.Entry(window, textvariable=var_m)
entry_m.place(x=220, y=270)


#1.3 Tolerance
tk.Label(window, text='Tolerance (ppm): ').place(x=430, y= 270)
var_t = tk.StringVar(value=10)
entry_t = tk.Entry(window, textvariable=var_t)
entry_t.place(x=550, y=270)

#1.4 Number of hits
tk.Label(window, text='Number of hits: ').place(x=430, y=310)
var_h = tk.StringVar(value=3)
entry_h = tk.Entry(window, textvariable=var_h)
entry_h.place(x=550, y=310)


#1.5 Adducts
tk.Label(window, text='Adducts: ').place(x=100, y= 430)
tk.Label(window, text='+Positive+').place(x=220, y= 330)
tk.Label(window, text='-Negative-').place(x=500, y= 370)

#1.5.1 Positive adducts
#1.5.1.1 Checklist 
class ChecklistBox(tk.Frame):
    def __init__(self, parent, choices, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.vars = []
        bg = self.cget("background")
        for choice in choices_p:
            var = tk.StringVar()
            self.vars.append(var)
            cb = tk.Checkbutton(self, var=var, text=choice,
                                onvalue=choice, offvalue="",
                                anchor="w", width=20, background=bg,
                                relief="flat", highlightthickness=0
            )
            cb.pack(side="top", fill="x", anchor="w")


    def getCheckedItems(self):
        values = []
        for var in self.vars:
            value =  var.get()
            if value:
                values.append(value)
        return values

#All positive adducts
choices_p = ('[M+H]+','[M+Na]+','[M+Na+H]2+','[M+K]+','[M+NH4]+','[M-H20+H]+','[2M+H]+','[M+2H]2+')
#place check list box
checklist_p = ChecklistBox(window, choices_p, bd=1, relief="sunken", background="white")
checklist_p.place(x=220,y=350)


#1.5.2 Negative adducts
class ChecklistBox(tk.Frame):
    def __init__(self, parent, choices, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.vars = []
        bg = self.cget("background")
        for choice in choices_n:
            var = tk.StringVar()
            self.vars.append(var)
            cb = tk.Checkbutton(self, var=var, text=choice,
                                onvalue=choice, offvalue="",
                                anchor="w", width=20, background=bg,
                                relief="flat", highlightthickness=0
            )
            cb.pack(side="top", fill="x", anchor="w")

    def getCheckedItems(self):
        values = []
        for var in self.vars:
            value =  var.get()
            if value:
                values.append(value)
        return values

#All negative adducts
choices_n = ('[M-H]-', '[M+Cl]-', '[M+Na-2H]-', '[M-H2O-H]-', '[M-2H]2-', '[2M-H]-')
checklist_n = ChecklistBox(window, choices_n, bd=1, relief="sunken", background="white")
checklist_n.place(x=500,y=390)


#1.6 Database
tk.Label(window, text='Database: ').place(x=100, y=550)
select_db = tk.StringVar(value='all_db')
tk.Radiobutton(window, text="HMDB", value='hmdb', variable=select_db).place(x=220, y=550)
tk.Radiobutton(window, text="ChEBI", value='chebi', variable=select_db).place(x=320, y=550)
tk.Radiobutton(window, text="Lipid Map", value='lm', variable=select_db).place(x=420, y=550)
tk.Radiobutton(window, text="3 Databases", value='all_db', variable=select_db).place(x=520, y=550)

#local database
tk.Label(window, text='Local Database:').place(x=100, y=580)
var_ld = tk.StringVar()
entry_ld = tk.Entry(window, textvariable=var_ld)
entry_ld.place(x=220, y=580)

#1.7 Sample
tk.Label(window, text='Simple(optinal):').place(x=100, y=610)
#tk.Label(window, text='(Uribe/Serum/CSF/Saliva/Feces/Sweat)', ).place(x=100, y=630)
var_sam = tk.StringVar()
entry_sam = tk.Entry(window, textvariable=var_sam)
entry_sam.place(x=220, y=610)
#**************************************************************************************************





#2. Search
#2.1 Adducts
adducts_info = [
['[M+H]+', 1.007276, 1],['[M+Na]+', 22.989218, 1],
['[M+Na+H]2+', 11.998247, 2], ['[M+K]+', 38.963158, 1],
['[M+NH4]+', 18.033823, 1],['[M-H20+H]+', -17.002740, 1], 
['[2M+H]+', 1.007276, 0.5],['[M+2H]2+', 1.007276, 2],
['[M-H]-', -1.007276, -1], ['[M+Cl]-', 34.969402, -1],
['[M+Na-2H]-', 20.974666, -1], ['[M-H2O-H]-', -19.01839, -1],
['[M-2H]2-', -1.007276, -2], ['[2M-H]-', -1.007276, -1/2]
]
#get the adducts that user selected
def get_adducts():
    adducts = []
    for i in range(len(adducts_info)):
        if adducts_info[i][0] in checklist_p.getCheckedItems():
            adducts.append(adducts_info[i])
        if adducts_info[i][0] in checklist_n.getCheckedItems():
            adducts.append(adducts_info[i])
    return adducts

#2.2 Database
def get_db():
    #if local db is string, then return the local db
    if var_ld.get() != '':
        db = var_ld.get()
    else:
        db = select_db.get()
    return db

#connect to the database  
con = sqlite3.connect('compounds.db')
cur = con.cursor() 

#2.3 Sample
def sample(db_name,sample):
    #select the rows that column 'sample' contains the sample name
    if sample != '':
        cur.execute('SELECT * FROM %s WHERE sample LIKE "%%%s%%"' % (db_name,sample))
        db = cur.fetchall()
    else:
        cur.execute('SELECT * FROM '+db_name)
        db = cur.fetchall()
    return db

#2.4 Input
def open_input(f_name):
    input = pd.read_csv(f_name)
    M = input.iloc[:,0].to_list()
    T = input.iloc[:,1].to_list()
    T_max, T_min = max(T), min(T)
    nor_t =  [(i-T_min)/(T_max-T_min)*1000 for i in T] #normalize the retention time
    return M,T, nor_t


#2.5 Main Function
# set the weight to determine the confidence score
t_weight, t_threshold, t_punish = 3/10, 0.3, -0.1
o_weight, sam_weight = 0.1, 0.1
m_weight = 1


M = [] #all the m/z values that query from input file
dflist = [] 
columns = ['m/z', 'Retention Time', 'InChIKey First Block', 'Accession', "Name", 'Mass', 'Theoretical m/z', 'PPM Error', 'Adduct', 'Source', 'Sample', 'MS/MS', 'Score']
df = pd.DataFrame(columns=columns)


# Get data for one mass
def get_data(db_name,left,right):
    sql = f'SELECT * FROM {db_name} where Mass between {left} and {right}' #select compouds based on m/z and tolerance
    cur.execute(sql)
    data = cur.fetchall()
    return data


def search():
#2.2.1 Query values from the user input
    M = open_input(var_m.get().strip(" "))
    tol = var_t.get()
    hits_num = int(var_h.get())   #get number of hits
    db = get_db()                 #selected database
    adducts = get_adducts()       #Get seleted adducts
 

#2.2.2filter
    num = 0 
    for adduct in adducts:
        for m, ori_t, t in zip(M[0], M[1], M[2]):
            theore_v  = abs((m - adduct[1])*adduct[2])
            tolerance = float(tol) * 0.000001 * theore_v
            left      = theore_v - tolerance
            right     = abs((m - adduct[1])*adduct[2]) + tolerance
            i = 0
            data = get_data(db, left, right)
            
            #wirte in dataframe(dflist)
            for row in data:   #mass in db that between left and right
                ref_rt = row[7]
                exp_mass = abs((row[3]+adduct[1])/adduct[2])
                ppm_error = abs(1000000*((exp_mass-m)/exp_mass))
                
                m_score = (1-(ppm_error/float(tol))) * m_weight
                
                #calculate the score of retention time
                if ref_rt:
                    rt_diff = abs((t - float(ref_rt))/float(ref_rt))
                    t_score = t_weight * rt_diff if rt_diff <= t_threshold else t_punish
                else:
                    t_score = 0
                
                #calculate the score of adduct    
                o_score = o_weight if adduct[0] in ('[M+H]+', '[M-H]-') else 0
                
                #score = str(t_score) + ', ' + str(o_score)
                score = float(m_score) + float(t_score) + float(o_score)
                
                compounds = pd.DataFrame(columns=columns)
                #calculate the score of sample type
                if ppm_error <= float(tol):
                    if var_sam.get() != '' and var_sam.get() in row[6]:
                        score += sam_weight
                    compounds.loc[i] = [m, t if var_sam.get() != '' else ori_t, row[0], row[1], row[2], row[3], exp_mass, ppm_error, adduct[0], row[4], row[6], row[5], score]
                    i += 1
                    dflist.append(compounds)
                    
            num += 1
            
    df = pd.concat(dflist)
    return df
#**************************************************************************************************"    






#3 Flitter
#3.1 Group
def group_df(df):
    df = df.sort_values(by=['Score'], ascending=True)
    df = df.groupby(['m/z', 'Retention Time']).head(3)
    #sort the dataframe by mz, if mz is the same, then sort by retention time, if retention time is the same, then sort by score
    df = df.sort_values(by=['m/z', 'Retention Time', 'Score'], ascending=[True, True, True])
    return df
    
#3.2 if the row has the same mz and rt with the previous row, add this row to previous row, seperate by '\n'
def merge_df(df):   
    #replace all the value to string
    result = df.astype(str)
    result = result.groupby(['m/z', 'Retention Time']).agg({'InChIKey First Block': '\n'.join, 'Accession': '\n'.join, "Name": '\n'.join, 'Mass': '\n'.join, 'Theoretical m/z': '\n'.join, 'PPM Error': '\n'.join, 'Adduct': '\n'.join, 'Source': '\n'.join, 'Sample': '\n'.join, 'MS/MS': '\n'.join, 'Score': '\n'.join})
    result = result.reset_index()
    return result 
#**************************************************************************************************"

    
    
    
    
#4. Plot
def result_plot(df, result):
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))

    #Fig 1, Distribution
    annotated = len(result)
    M = open_input(var_m.get())
    unannotated = len(M[0]) - annotated
    hmdb = chebi = lm = 0
    #for source in df['Source']:, if hmdb in source, then hmdb += 1
    for source in result['Source']:
        if 'hmdb' in source:
            hmdb += 1
        if 'chebi' in source:
            chebi += 1
        if 'lm' in source:
            lm += 1
    #plot bar chart that show the distribution of database and annotated vs unannotated
    axs[0,0].bar(['Annotated', 'Unannotated', 'HMDB', 'ChEBI',  'LipidMaps'], [annotated, unannotated, hmdb, chebi, lm], color=['#79E078', '#6CA26C', '#FAC694', '#BA6364', '#6E83BE'])
    #make the lavel horizontal
    axs[0,0].tick_params(axis='x', rotation=35)
    #axs[0,0].set_title('Distribution', fontweight='bold')
    axs[0,0].set_ylabel('Number of Compounds')
    
    
    
    #Fig 2, annotated hexbin plot, mass vs retention time, x is mass, y is retention time, color is number of compounds
    #axs[0,1].hexbin(result['m/z'], result['Retention Time'], gridsize=20, cmap='Greens')
    sns.kdeplot(result['m/z'], result['Retention Time'], ax=axs[0,1], cmap='Greens', shade=True, shade_lowest=False)
    #axs[0,1].set_title('Annotated', fontweight='bold')
    axs[0,1].set_xlabel('m/z')  
    axs[0,1].set_ylabel('Retention Time')
    axs[0,1].set_title('Annotated', fontweight='bold')

    
    
    #Fig 3, unannotated hexbin plot, mass vs retention time, x is mass, y is retention time, color is number of compounds
    M = open_input(var_m.get())
    sns.kdeplot(M[0], M[1], ax=axs[0,2], cmap='Greys', shade=True, shade_lowest=False)
    #set the x and y label
    axs[0,2].set_xlabel('m/z')
    axs[0,2].set_ylabel('Retention Time')
    axs[0,2].set_title('Unannotated', fontweight='bold')
    
    
    #Fig 4, ppm error plot box seperate by database
    hmdb_list = []
    chebi_list = []
    lm_list = []
    for i in range(len(df)):
        if 'hmdb' in df['Source'][i]:
            hmdb_list.append(df['PPM Error'][i])
        if 'chebi' in df['Source'][i]:
            chebi_list.append(df['PPM Error'][i])
        if 'lm' in df['Source'][i]:
            lm_list.append(df['PPM Error'][i])
    sns.boxplot(data=[hmdb_list, chebi_list, lm_list], ax=axs[1,0], palette='crest')
    #set the x and y label
    axs[1,0].tick_params(axis='x', rotation=35)
    axs[1,0].set_xticklabels(['HMDB', 'ChEBI', 'LipidMaps'])
    axs[1,0].set_ylabel('PPM Error')
    #axs[1,0].set_title(, fontweight='bold')
    
    
    
    #Fig 5, adduct pie chart
    adduct = df['Adduct'].value_counts()
    axs[1,1].pie(adduct, labels=adduct.index, autopct='%1.1f%%', startangle=90, colors=['#6CA26C', '#FAC694', '#BA6364', '#6E83BE'])
    #axs[1,1].set_title('Adduct Type')
    
    #Fig 6, ppm error plot box seperate by adduct type
    sns.boxplot(x='Adduct', y='PPM Error', data=df, ax=axs[1,2], palette='crest')
    #axs[1,2].set_title('PPM Error')
    
    
    
    #Canvas 2
    fig2, ax2 = plt.subplots(1,3, figsize=(15, 5))
    #Fig 6, hexbin of HMDB, mass vs retention time, x is mass, y is retention time, color is number of compounds
    hmdb = df[df['Source'].str.contains('hmdb')]
    ax2[0].hexbin(hmdb['m/z'], hmdb['Retention Time'], gridsize=20, cmap='YlOrBr')
    #set the title: HMDB and color is #FAC694, and bold
    ax2[0].set_title('HMDB', color='#F3AB7B', fontweight='bold')
    ax2[0].set_xlabel('m/z')
    ax2[0].set_ylabel('Retention Time')
    
    
    #Fig 7, hexbin of ChEBI, mass vs retention time, x is mass, y is retention time, color is number of compounds
    chebi = df[df['Source'].str.contains('chebi')]
    ax2[1].hexbin(chebi['m/z'], chebi['Retention Time'], gridsize=20, cmap='rocket_r')
    ax2[1].set_title('ChEBI', color='#BA6364', fontweight='bold')
    ax2[1].set_xlabel('m/z')
    ax2[1].set_ylabel('Retention Time')
    
    #Fig 8, hexbin of LipidMaps, mass vs retention time, x is mass, y is retention time, color is number of compounds
    lm = df[df['Source'].str.contains('lm')]
    ax2[2].hexbin(lm['m/z'], lm['Retention Time'], gridsize=20, cmap='Blues')
    ax2[2].set_title('LipidMaps', color='#6E83BE', fontweight='bold')
    ax2[2].set_xlabel('m/z')
    ax2[2].set_ylabel('Retention Time')

    plt.show()
#**********************************************************************************************************************





#4 Search Button
def main():
    df = search()
    #print(df)
    df = group_df(df)
    df.to_csv('no_filter.csv', index=False)
    df = df.reset_index(drop=True)
    
    o_file = 'lime_' + var_m.get()
    result = merge_df(df)
    result.to_csv(o_file, index=False)
    result = pd.read_csv(o_file)
    tk.messagebox.showwarning(message="file ("+o_file+") has been generated")
    
    result_plot(df, result)
    
    #print("\n\n\n")
    print('\n\n\nProcess completed successfully!')
    print(" _._     _,-'\"`-._")
    print("(,-.`._,'(       |\\`-/|")
    print("    `-.-' \\ )-`( , o o)")
    print("          `-    \\`_`\"'-")



    
#set the button size and background color
btn = tk.Button(window, text='Search', width=10, height=2, command=main)
btn.place(x=500, y=590)
df = pd.DataFrame(columns=columns)

window.mainloop()
#con.close()