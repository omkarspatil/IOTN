import web
import pdfkit
import base64
import re
import pdfkit
import os
import json
import shutil
import subprocess
from subprocess import STDOUT

urls = (
    '/', 'index',
    '/case_step_1','case_step_1',
    '/case_step_2','case_step_2',
    '/case_step_3','case_step_3',
    '/case_step_4','case_step_4',
    '/case_step_5_init','case_step_5_init',
    '/case_step_5_final','case_step_5_final'
)


db = web.database(dbn='mysql', user='root', pw='beproject#2016', db='iotn')

def boolEval(str):
	if str=='true':
		return True
	elif str=='false':
		return False
	else:
		return None

class index:
    def GET(self):
        return "Hello, world!"

class case_step_1:
	def POST(self):
		web.header('Access-Control-Allow-Origin',      '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		case_step1_data = web.input()
		signature=case_step1_data.signature
		image_data = re.sub('^data:image/.+;base64,', '', signature).decode('base64')
		case_id=db.insert('cases', patient_first_name=case_step1_data.first_name,patient_last_name=case_step1_data.last_name,patient_gender=case_step1_data.gender,patient_date_of_birth=case_step1_data.dob,patient_age=case_step1_data.age,date_of_study=case_step1_data.dos,time_of_study=case_step1_data.tos,patient_email=case_step1_data.email,patient_mobile_number=case_step1_data.mobile_number)
		with open("/home/ubuntu/IOTN/data/ConsentForms/sign"+str(case_id)+".png", "wb") as fh:
			fh.write(image_data)
		#Generate and store PDF Consent
		with open("consent_template.html", "rt") as fin:
			with open("/home/ubuntu/IOTN/data/ConsentForms/"+str(case_id)+".html","wt") as fout:
				for line in fin:
					fout.write(line.replace('~NAME~', case_step1_data.first_name+" "+case_step1_data.last_name).replace('~AGE~',case_step1_data.age).replace('~DATE~',str(case_step1_data.dos)).replace('~SIGN~',signature))
		pdfkit.from_file("/home/ubuntu/IOTN/data/ConsentForms/"+str(case_id)+".html","/home/ubuntu/IOTN/data/ConsentForms/"+str(case_id)+".pdf")
		db.update('cases',where="case_id ="+str(case_id),patient_consent_form_url="/home/ubuntu/IOTN/data/ConsentForms/"+str(case_id)+".pdf")
		os.remove("/home/ubuntu/IOTN/data/ConsentForms/"+str(case_id)+".html")
		os.remove("/home/ubuntu/IOTN/data/ConsentForms/sign"+str(case_id)+".png")
		if case_id is not None:
			result={"result":"Success","case_id":case_id}
			return json.dumps(result)

class case_step_2:
	def POST(self):
		web.header('Access-Control-Allow-Origin',      '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		case_step2_data = web.input()
		print str(case_step2_data)
		rows=db.update('cases', where="case_id ="+case_step2_data.case_id, chief_complaint=case_step2_data.cheif_complaint, past_medical_history=case_step2_data.past_medical_history,past_dental_history=case_step2_data.past_dental_history)
		if rows==1:
			result={"result":"Success"}
			return json.dumps(result)

class case_step_3:
	def POST(self):
		web.header('Access-Control-Allow-Origin',      '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		case_step3_data = web.input()
		print str(case_step3_data)
		rows=db.update('cases', where="case_id ="+case_step3_data.case_id, overjet=case_step3_data.overjet, overbite=case_step3_data.overbite,crossbite=boolEval(case_step3_data.crossbite),
						crossbite_region=case_step3_data.crossbite_region,congenital_anomalies=boolEval(case_step3_data.congenital_anomalies),congenital_anomalies_region=case_step3_data.congenital_anomalies_region,
						supernumerary_teeth=boolEval(case_step3_data.supernumerary_teeth),supernumerary_teeth_region=case_step3_data.supernumerary_teeth_region,impacted_teeth=boolEval(case_step3_data.impacted_teeth),
						impacted_teeth_region=case_step3_data.impacted_teeth_region,dental_health_component_score=case_step3_data.dhc_score)
		if rows==1:
			result={"result":"Success"}
			return json.dumps(result)

class case_step_4:
	def POST(self):
		print "Here in step 4"
		web.header('Access-Control-Allow-Origin',     '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		case_step4_data = web.input()
		print str(case_step4_data)
		rows=db.update('cases', where="case_id ="+case_step4_data.case_id,iotn_test_image_url="/var/www/html/omkar/iotn/croppic/"+case_step4_data.imageURL)
		if rows==1:
			result={"result":"Success"}
			return json.dumps(result)

class case_step_5_init:
	def POST(self):
		web.header('Access-Control-Allow-Origin',     '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		case_step5_data = web.input()
		results = db.select('cases', what="iotn_test_image_url", where="case_id ="+case_step5_data.case_id)
		print results
		result=results[0]["iotn_test_image_url"]
		print result
		filename=result.split("TestingImages/",1)[1] 
		filenamejpg=case_step5_data.case_id+".jpg"
		#Rename and copy this image to TestingImages
		print filenamejpg
		shutil.copy2(result,"/home/ubuntu/IOTN/data/TestingImages/"+filenamejpg)
		os.chdir("/home/ubuntu/IOTN/bin")
		finalresults=subprocess.check_output('xvfb-run -a java -jar iotn-0.0.1-SNAPSHOT-jar-with-dependencies.jar '+case_step5_data.case_id,shell=True,stderr=STDOUT,universal_newlines=True).rstrip('\n')
		iotnresult=finalresults.split("?\n")[1]
		print iotnresult
		os.chdir("/home/ubuntu/IOTN/web")
		jsonobj=json.loads(iotnresult)
		rows=db.update('cases', where="case_id ="+case_step5_data.case_id,automated_iotn_score=jsonobj["IOTN"],symmetry_score=jsonobj["Symmetry"],overbite_score=jsonobj["Overbite"],alignment_score=jsonobj["Alignment"],iotn_output_image_1_url="/home/ubuntu/IOTN/data/TestingOutput/"+case_step5_data.case_id+"finalthresholded.png",iotn_output_image_2_url="/home/ubuntu/IOTN/data/TestingOutput/"+case_step5_data.case_id+"finalaxesthresholded.png")
		result_json={"IOTN":jsonobj["IOTN"],"Alignment":jsonobj["Alignment"],"Overbite":jsonobj["Overbite"],"Symmetry":jsonobj["Symmetry"]}
		return json.dumps(result_json)

class case_step_5_final:
	def POST(self):
		web.header('Access-Control-Allow-Origin',     '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		case_step5_data = web.input()
		#generate pdf reports and send out via email
		rows=db.update('cases', where="case_id ="+case_step5_data.case_id,manually_graded_iotn_score=case_step5_data.manual_iotn)
		results = db.select('cases', where="case_id ="+case_step5_data.case_id)
		result=results[0]
		with open("report_template.html", "rt") as fin:
			with open("/home/ubuntu/IOTN/data/PDFReports/"+case_step5_data.case_id+"_iotn_report.html","wt") as fout:
				for line in fin:
					fout.write(line.replace('~NAME~', result["patient_first_name"]+" "+result["patient_last_name"]).replace('~DOB~',str(result["patient_date_of_birth"])).replace('~AGE~',str(result["patient_age"])).replace('~GENDER~',str(result["patient_gender"])).replace('~DOS~',str(result["date_of_study"])).replace('~TOS~',str(result["time_of_study"])).replace('~EMAIL~',str(result["patient_email"])).replace('~MOBILE~',str(result["patient_mobile_number"]))
						.replace('~CHIEF_COMPLAINT~',str(result["chief_complaint"])).replace('~PAST_MEDICAL_HISTORY~',str(result["past_medical_history"])).replace('~PAST_DENTAL_HISTORY~',str(result["past_dental_history"])).replace('~OVERBITE~',str(result["overbite"]))
						.replace('~OVERJET~',str(result["overjet"])).replace('~CROSSBITE~',str(result["crossbite"])).replace('~CROSSBITE_REGION~',str(result["crossbite_region"])).replace('~CONGENITAL_ANOMALIES~',str(result["congenital_anomalies"])).replace('~CONGENITAL_ANOMALIES_REGION~',str(result["congenital_anomalies_region"]))
						.replace('~SUPERNUMERARY_TEETH~',str(result["supernumerary_teeth"])).replace('~SUPERNUMERARY_TEETH_REGION~',str(result["congenital_anomalies_region"])).replace('~IMPACTED_TEETH~',str(result["impacted_teeth"])).replace('~IMPACTED_TEETH_REGION~',str(result["impacted_teeth_region"])).replace('~DHC_SCORE~',str(result["dental_health_component_score"]))
						.replace('~IOTN_TEST_IMAGE~',str(result["iotn_test_image_url"])).replace('~IOTN_OUT_IMAGE_1~',str(result["iotn_output_image_1_url"])).replace('~IOTN_OUT_IMAGE_2~',str(result["iotn_output_image_2_url"])).replace('~IOTN_AUTOMATED_SCORE~',str(result["automated_iotn_score"]))
						.replace('~IOTN_MANUAL_GRADING_SCORE~',str(result["manually_graded_iotn_score"])).replace('~AXIS~',str(result["alignment_score"])).replace('~SYMMETRY~',str(result["symmetry_score"])).replace('~OVERBITE_SCORE~',str(result["overbite_score"])))
		pdfkit.from_file("/home/ubuntu/IOTN/data/PDFReports/"+case_step5_data.case_id+"_iotn_report.html","/home/ubuntu/IOTN/data/PDFReports/"+case_step5_data.case_id+"_iotn_report.pdf")
		db.update('cases',where="case_id ="+case_step5_data.case_id,pdf_case_report_url="/home/ubuntu/IOTN/data/PDFReports/"+case_step5_data.case_id+"_iotn_report.pdf")
		os.remove("/home/ubuntu/IOTN/data/PDFReports/"+case_step5_data.case_id+"_iotn_report.html")
		finalresults=subprocess.check_output("./send.sh '"+str(result["patient_email"])+"' 'prerana.d12@gmail.com' 'IOTN Report for "+result["patient_first_name"]+" "+result["patient_last_name"]+"(Case number "+str(case_step5_data.case_id)+")' 'Hi "+result["patient_first_name"]+",\nPlease find attached with this email the reports from the IOTN study. Thanks for your co-operative participation.\n\nRegards,\nDr. Prerana Dubey' '"+str(result["patient_consent_form_url"])+"' '"+str(result["pdf_case_report_url"])+"'",shell=True,stderr=STDOUT,universal_newlines=True).rstrip('\n')
		result={"result":"Success"}
		return json.dumps(result)

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
