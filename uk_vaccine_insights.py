'''Code to gain insights on UK Vaccine programme'''

import numpy as np
import pandas as pd
from requests import get
import matplotlib.pyplot as plt

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

def get_data(url):
    '''Function to get data from API endpoint given the endpoint URL'''
    response = get(endpoint, timeout=10)
    
    if response.status_code >= 400:
        raise RuntimeError(f'Request failed: { response.text }')
        
    return response.json()

#here, code can be edited to get any data you want for certain filters, see:
#https://coronavirus.data.gov.uk/details/developers-guide

endpoint = (
        'https://api.coronavirus.data.gov.uk/v1/data?'
        'filters=areaType=overview&'
        'structure={"date":"date","newCases":"newCasesByPublishDate", "newAdmissions":"newAdmissions"}'
    )
    
data = get_data(endpoint)
print("Api call successful...")


###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

'''First, let's plot cases and admissions and investigate'''

df_columns = ['date', 'no_cases','new_admissions']
df = pd.DataFrame(columns = df_columns)

#loop over JSON output and turn into DataFrame
for i in range(len(data['data'])):
    df = df.append(
                    pd.Series([
                    data['data'][i]['date'], 
                    data['data'][i]['newCases'],
                    data['data'][i]['newAdmissions']
                    ], 
                    index = df_columns), 
                    ignore_index = True)
                    
df = df.set_index('date')
df.index = pd.to_datetime(df.index)

df.head(5)

#define dates to split the data by. 
#these dates roughly relate to mass testing uptake high and start of vaccine impact
first_cut = '2020-06-20'
second_cut = '2021-05-20'

#Double plot the cases and admissions over time

# create figure and axis objects with subplots()
fig,ax = plt.subplots()
# make a plot
ax.plot(df.index, df.no_cases, color="blue")
# set x-axis label
ax.set_xlabel("Date",fontsize=14)
# set y-axis label
ax.set_ylabel("No. Cases",color="blue",fontsize=14)
# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(df.index, df.new_admissions,color="red")
ax2.set_ylabel("No. Admissions",color="red",fontsize=14)
fig.autofmt_xdate()
plt.savefig("casesandadmissions.png",bbox_inches='tight')
plt.show()

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

#investigate the correlation
#plot the correlations
#mass testing not available until after first peak, so only consider points after this...
df_corr = df.loc[df.index > first_cut]

#normalise cases and admissions to explore correlations
print(" ")
print("----------------------------------------------------------")
print("Max number of cases:")
print(max(df_corr['no_cases']))
print("----------------------------------------------------------")
print(" ")
df_corr.new_admissions.fillna(0,inplace=True)
print(" ")
print("----------------------------------------------------------")
print("Max number of admissions:")
print(max(df_corr['new_admissions']))
print("----------------------------------------------------------")
print(" ")

#normalise cases and admissions
df_corr["normalised_cases"] = df_corr.no_cases/61757
df_corr["normalised_admissions"] = df_corr.new_admissions/4134

df_corr1 = df_corr.loc[df_corr.index < second_cut]
df_corr2 = df_corr.loc[second_cut < df_corr.index]

fig_corr = plt.Figure()

#plot correlation
plt.scatter(df_corr1.normalised_cases, df_corr1.normalised_admissions, color='red',label="Pre " + second_cut)
plt.scatter(df_corr2.normalised_cases, df_corr2.normalised_admissions, color='blue',label="Post "+second_cut)

#fit linear model to get metric for correlation
m1,c1 = np.polyfit(df_corr1.normalised_cases.to_numpy(dtype=float),df_corr1.normalised_admissions.to_numpy(dtype=float), deg=1) 
m2,c2 = np.polyfit(df_corr2.normalised_cases.to_numpy(dtype=float),df_corr2.normalised_admissions.to_numpy(dtype=float), deg=1)  

plt.plot(df_corr1.normalised_cases, m1*df_corr1.normalised_cases + c1, color='red', label="$C_1$="+ "{:.1f}".format(m1))
plt.plot(df_corr2.normalised_cases, m2*df_corr2.normalised_cases + c2, color='blue', label="$C_2=$"+ "{:.1f}".format(m2))

#label axes
plt.xlabel("Normalised Cases")
plt.ylabel("Normalised Admissions")

plt.legend()
plt.show()

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################


'''Next, let's look at the vaccines...'''

#change endpoint to get vaccine data
#https://coronavirus.data.gov.uk/details/developers-guide

endpoint = (
        'https://api.coronavirus.data.gov.uk/v1/data?'
        'filters=areaType=overview&'
        'structure={"date":"date","cumPeopleVaccinatedCompleteByPublishDate":"cumPeopleVaccinatedCompleteByPublishDate", "cumPeopleVaccinatedFirstDoseByPublishDate":"cumPeopleVaccinatedFirstDoseByPublishDate"}'
    )
    
data_vacc = get_data(endpoint)
print("Api call successful...")


#Source of following hard coded values:
#https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland

print(" ")
print("----------------------------------------------------------")
print("UK population")
uk_pop = 67081234
print(uk_pop)
print(" ")

print(" ")
print("----------------------------------------------------------")
print("No. under 18's")
under_18s = 14191190
print(under_18s)
print((under_18s/uk_pop)*100)
print(" ")

print(" ")
print("----------------------------------------------------------")
print("No. Double Jabbed")
double_jabbed = data_vacc['data'][0]['cumPeopleVaccinatedCompleteByPublishDate']
print(double_jabbed)
print((double_jabbed/uk_pop)*100)
print(" ")
print("----------------------------------------------------------")
print(" ")
print("----------------------------------------------------------")
print("No. Single Jabbed")
single_only = data_vacc['data'][0]['cumPeopleVaccinatedFirstDoseByPublishDate'] - data_vacc['data'][0]['cumPeopleVaccinatedCompleteByPublishDate']
print(single_only)
print((single_only/uk_pop)*100)
print(" ")
print("----------------------------------------------------------")
print(" ")
print("----------------------------------------------------------")
print("No. Unvaccinated")
unvaccinated = uk_pop - (under_18s + double_jabbed + single_only)
print(unvaccinated)
print((unvaccinated/uk_pop)*100)
print(" ")
print("----------------------------------------------------------")

fig_vac = plt.figure(figsize=[14.0, 4.8])

plt.barh([0], (double_jabbed/uk_pop)*100, color="forestgreen", label = "x2 Dose")
plt.barh([0], (single_only/uk_pop)*100, left= (double_jabbed/uk_pop)*100, color="darkseagreen", label = "x1 Dose")
plt.barh([0], (under_18s/uk_pop)*100, left = (double_jabbed/uk_pop)*100 + (single_only/uk_pop)*100, color="royalblue", label = "Under 18")
plt.barh([0], (unvaccinated/uk_pop)*100, left = (double_jabbed/uk_pop)*100 + (single_only/uk_pop)*100 + (under_18s/uk_pop)*100, color="lightcoral", label = "Unvaccinated")
plt.legend(fontsize=14)
plt.yticks([])
plt.xlim(0,100)
plt.ylim(0,0.25)
plt.xlabel("% of Population", fontsize=14)

plt.text(28, 0.12, "55%", rotation='horizontal', fontsize=22)
plt.text(25, 0.10, "~37m", rotation='horizontal', fontsize=22)
plt.text(25, 0.08, r"$\rightarrow$ ~7.8m", rotation='horizontal', fontsize=22)

plt.text(58,0.12, "14%",rotation='horizontal', fontsize=22)
plt.text(55, 0.10, "~9.6m",rotation='horizontal', fontsize=22)
plt.text(55, 0.08, r"$\rightarrow$ ~6.2m", rotation='horizontal', fontsize=22)

plt.text(76,0.12, "21%",rotation='horizontal', fontsize=22)
plt.text(73, 0.10, "~14.2m",rotation='horizontal', fontsize=22)

plt.text(93, 0.12, "10%",rotation='horizontal', fontsize=22)
plt.text(90.5, 0.10, "~6.4m",rotation='horizontal', fontsize=22)

plt.show()

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################



'''Next, let's look at vaccine effectiveness'''


###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################


#https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1005085/Vaccine_surveillance_report_-_week_29.pdf

#Vaccine effectiveness against symptomatic disease for Alpha and Delta variants
d = {'Vaccine Status': ["Dose 1", "Dose 2"], 'Alpha': [49, 89], 'Delta': [35, 79]}
df_VE = pd.DataFrame(data=d)
df_VE


fig_eff_d = plt.figure()


plt.bar([0], df_VE["Alpha"][1], color="lightblue", label = "x2 Dose")
plt.bar([0], df_VE["Alpha"][0], color="royalblue", label = "x1 Dose")

plt.bar([1], df_VE["Delta"][1], color="lightblue") #, label = "Dose2")
plt.bar([1], df_VE["Delta"][0], color="royalblue") #, label = "Dose 1")

plt.text(-0.1, 30, str(df_VE["Alpha"][0])+"%", rotation='horizontal', fontsize=22)
plt.text(-0.1, 70, str(df_VE["Alpha"][1])+"%",rotation='horizontal', fontsize=22)
plt.text(0.9, 20, str(df_VE["Delta"][0])+"%",rotation='horizontal', fontsize=22)
plt.text(0.9, 60, str(df_VE["Delta"][1])+"%",rotation='horizontal', fontsize=22)

plt.legend()
plt.xticks([0,1],["Alpha","Delta"], fontsize=14)
plt.title("Vaccine effectiveness against symptomatic disease", fontsize=14)
plt.ylabel("% Effectiveness", fontsize=14)
plt.ylim(0,100)#
plt.show()

#Vaccine effectiveness against hospitalisation for Alpha and Delta variants
d = {'Vaccine Status': ["Dose 1", "Dose 2"], 'Alpha': [78, 93], 'Delta': [80, 96]}
df_VEH = pd.DataFrame(data=d)
df_VEH

fig_eff_d = plt.figure()


plt.bar([0], df_VEH["Alpha"][1], color="lightblue", label = "x2 Dose")
plt.bar([0], df_VEH["Alpha"][0], color="royalblue", label = "x1 Dose")

plt.bar([1], df_VEH["Delta"][1], color="lightblue") #, label = "Dose2")
plt.bar([1], df_VEH["Delta"][0], color="royalblue") #, label = "Dose 1")

plt.text(-0.1, 50, str(df_VEH["Alpha"][0])+"%", rotation='horizontal', fontsize=22)
plt.text(-0.1, 82, str(df_VEH["Alpha"][1])+"%",rotation='horizontal', fontsize=22)
plt.text(0.9, 50, str(df_VEH["Delta"][0])+"%",rotation='horizontal', fontsize=22)
plt.text(0.9, 85, str(df_VEH["Delta"][1])+"%",rotation='horizontal', fontsize=22)

#plt.legend()
plt.xticks([0,1],["Alpha","Delta"], fontsize=14)
plt.title("Vaccine effectiveness against hospitalisation", fontsize=14)
plt.ylabel("% Effectiveness", fontsize=14)
plt.ylim(0,100)
plt.show()

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################