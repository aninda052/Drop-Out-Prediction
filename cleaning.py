import pandas as pd
#import math
from collections import Counter
import time


data=pd.read_csv('.data/studentinfo.csv')
grade_data=pd.read_csv('.data/csestudentsgrades.csv')

data['dif_ssc_hsc']=0
data['dif_hsc_uni']=0
data['drop_out']="reguler"

for i in range(len(data)):

	print(i)                                         

	total_conv=data['hsctotal'][i]
	try:
		total_conv=float(total_conv)
	except ValueError:
		total_conv=float(data['hscgrade'][i])         
	data['hsctotal'][i]=total_conv

	total_conv=data['ssctotal'][i]
	try:
		total_conv=float(total_conv)
	except ValueError:
		total_conv=float(data['sscgrade'][i])         
	data['ssctotal'][i]=total_conv


	tmp=(data['hscyear'][i]-data['sscyear'][i])-2
	if str(tmp)!= 'nan':
		
		data['dif_ssc_hsc'][i]=int(tmp)
		print(data['new_id'][i],tmp)

	tmp=(data['batch'][i]/10)-data['hscyear'][i]
	if str(tmp)!='nan':
		data['dif_hsc_uni'][i]=int(tmp)

	#print(i,' - ',data['dif_hsc_uni'][i])


data=data.drop(['sscgrade','hscgrade','dobday','dobyear','dobmon','fathermonin','sscins','sscboard','sscsub','data','hscboard','hscsub'],axis=1)
data=data.dropna()
data=data.reset_index(drop=True)



def cgpa_calculation(data,all_subjects):

	new_grade_point=sum(data['gp']*data['credits'])

	sub=set(data['course_code'])
	new_sub=list(sub.difference(all_subjects))

	mask=data['course_code'].isin(new_sub)
	new_credit_earn=sum(data[mask]['credits'])
	
	fail = len(data['course_code'][data['grade']=='F']) 

	return new_sub,new_grade_point,new_credit_earn,fail

for i in range(16):
	tmp='semester'+str(i+1)+'_cgpa'
	data[tmp]=0.0
	tmp='semester'+str(i+1)+'_fail'
	data[tmp]=0


delet_row=[]

for i in range(len(data['new_id'])):
	print('-',i)
	t = time.time()
	ID=data['new_id'][i]
	search_id=grade_data['new_id']==ID
	if (search_id.any() == False):
		delet_row.append(i)
		continue

	id_info= grade_data[search_id]
	Batch_list= list(set(id_info['semester_id']))
	batch_len=len(Batch_list)

	if batch_len>16:
		delet_row.append(i)
		continue
	Batch_list.sort()
	#print (ID)

	id_subject=set()
	grade_point=0.0
	credit_earn=0.0
	total_fail=0
	mark=0

	for j in range(batch_len):
		batch=Batch_list[j]
		t = time.time()
		sub,gp,cre,fail= cgpa_calculation(id_info[id_info['semester_id']==batch],id_subject)
		id_subject.update(sub)
		grade_point+=gp
		credit_earn+=cre
		total_fail+=fail

		tmp='semester'+str(j+1)+'_cgpa'
		if grade_point <2 :
			mark=0.0
		else :
			mark=grade_point/credit_earn

		data[tmp][i]=mark

		tmp1='semester'+str(j+1)+'_fail'
		data[tmp1][i]=fail

	if batch_len<16:
		for j in range(batch_len,16):
			tmp='semester'+str(j+1)+'_cgpa'
			data[tmp][i]=mark

		
	if (Batch_list[batch_len-1]<41 and  credit_earn<130) or (batch_len<3 and total_fail>=3): 
		data['drop_out'][i]="dropOut"

	#print ("%.3f" % (time.time()-t))

data.drop(data.index[delet_row],inplace=True)
data.to_csv('cleanData.csv',sep=',',index=False)	

