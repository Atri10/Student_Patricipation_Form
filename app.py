import logging
import requests
from flask import Flask, render_template, request
import re, gspread,uuid,random
from flask_mail import Mail, Message
from Paytm.paytm_checksum import generate_checksum, verify_checksum

app = Flask (__name__)
mail = Mail (app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'atri.codes369@gmail.com'
app.config['MAIL_PASSWORD'] = 'Iamwayne147'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail (app)

data = ["", "", "Use PDPU Email", ""]
values = ["", "", "", ""]
MERCHANT_ID = "PVJtrP40816538758018"
MERCHANT_KEY = "xOmgiv!ym!BuZdce"
WEBSITE_NAME = "WEBSTAGING"
INDUSTRY_TYPE_ID = "Retail"
BASE_URL = "https://securegw-stage.paytm.in"
amount = 50
order_id = uuid.uuid4()
custo_id = random.randrange(10000,99999)


@app.route ('/', methods=['GET', 'POST'])
def hello_world () :
    return render_template ("main.html", LIST=data, val=values)



@app.route ('/validator', methods=['GET', 'POST'])
def validator () :
    Name = request.form['Name']
    Rolno = request.form['RN']
    eemail = request.form['Mail']
    contact = request.form['CNT']
    values[0] = Name
    values[1] = Rolno
    values[2] = eemail
    values[3] = contact
    transaction_data = {
        "MID": MERCHANT_ID,
        "WEBSITE": WEBSITE_NAME,
        "INDUSTRY_TYPE_ID": INDUSTRY_TYPE_ID,
        "ORDER_ID": str(order_id),
        "CUST_ID": str(custo_id),
        "TXN_AMOUNT": str(amount),
        "CHANNEL_ID": "WEB",
        "MOBILE_NO": values[3],
        "EMAIL": values[2],
        "CALLBACK_URL": "http://127.0.0.1:5000/callback"
    }

    # Generate checksum hash
    transaction_data["CHECKSUMHASH"] = generate_checksum (transaction_data, MERCHANT_KEY)
    logging.info ("Request params: {transaction_data}".format (transaction_data=transaction_data))
    url = BASE_URL + '/theia/processTransaction'


    def Emailchecker ( str ) :
        ismail = re.match ('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', str)
        if ismail != None :
            return True
        else :
            return False

    def sheetupdater () :
        access = gspread.service_account(filename ='CRE.json')
        key = access.open_by_key('1KDUJaDpHfijy9agCEtaEICOsma4avdzinw7l9KFr-LM')
        sheet = key.sheet1
        info = [Name,Rolno,eemail,contact]
        sheet.append_row(info)

    def mailsender () :
        msg = Message (
            'Workshop Form',
            sender='atri.codes369@gmail.com',
            recipients=[eemail])
        msg.body = 'Your filled form is shown below'
        msg.html = render_template ("main.html", LIST=data, val=values)
        mail.send (msg)

    def inputscleaner():
        values[0] = ""
        values[1] = ""
        values[2] = ""
        values[3] = ""


    l = len (contact)
    dgt = contact.isdigit()
    print (Name)
    if (Name == "") :
        values[0] = ""
        s = "Name is Empty"
        data[0] = s
        return render_template ("main.html", LIST=data, val=values)
    elif (Rolno == "") :
        values[1] = ""
        s = "Roll Number is Empty"
        data[1] = s
        return render_template ("main.html", LIST=data, val=values)
    elif (eemail == "" or Emailchecker (eemail) == False) :
        values[2] = ""
        s = "Enter Mail Correctly"
        data[2] = s
        return render_template ("main.html", LIST=data, val=values)
    elif (contact == "" or l < 10 or l > 10 or dgt == False) :
        values[3] = ""
        s = "Enter Number correctly"
        data[3] = s
        return render_template ("main.html", LIST=data, val=values)
    else :
        try :
            mailsender ( )
            sheetupdater ( )
            inputscleaner()
            print (Name)
            return render_template ("REdirector.html", dic=transaction_data, url=url)
        except :
            inputscleaner ( )
            return render_template ("Error_page.html")




@app.route('/callback', methods=["GET", "POST"])
def callback():
    try:
         callback_response = request.form.to_dict()
         logging.info("Transaction response: {callback_response}".format(callback_response=callback_response))
         checksum_verification_status = verify_checksum(callback_response, MERCHANT_KEY,callback_response.get("CHECKSUMHASH"))
         logging.info("checksum_verification_status: {check_status}".format(check_status=checksum_verification_status))
         transaction_verify_payload = {
                "MID": callback_response.get("MID"),
                "ORDERID": callback_response.get("ORDERID"),
                "CHECKSUMHASH": callback_response.get("CHECKSUMHASH")
                 }
         url = BASE_URL + '/order/status'
         verification_response = requests.post(url=url, json=transaction_verify_payload)
         logging.info("Verification response: {verification_response}".format(verification_response=verification_response.json()))
         return render_template("thanks_success.html")
    except :
         return render_template ("Error_page.html")




if __name__ == '__main__' :
    app.run (debug=True)
