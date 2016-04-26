import datetime
import requests
import tempfile

from flask import Blueprint, request, make_response, current_app

from config.default import WKHTML_BINARY


api = Blueprint('api', __name__)

DEBUG_M = "ashishthedev@gmail.com"

def urltopdf(url, delayms=200):
    #with open("/tmp/o.pdf", "w+") as tpdf:
    with tempfile.NamedTemporaryFile(delete=False) as tpdf:
        cmd=[]
        cmd.append(WKHTML_BINARY)
        cmd.extend(["--viewport-size", "8000x800",
            "-O", "Landscape",
             "--no-stop-slow-scripts",
             "--javascript-delay", str(delayms),
            url, tpdf.name])
        current_app.logger.info(datetime.datetime.now())
        current_app.logger.info("cmd=\n{}".format(" ".join(cmd)))
        import subprocess
        subprocess.call(cmd)
        resultingPdfBinContents = tpdf.read()
        return resultingPdfBinContents


def FetchTitle(weburl):
    r = requests.get(weburl)
    r.encoding = 'utf-8'
    html = r.text
    start = html.find("<title>")
    end = html.find("</title>")
    if start == -1 or end == -1:
        current_app.logger.info("Cannot parse title")
        return None
    else:
        title = html[start + len("<title>"): end].strip()
        current_app.logger.info("Parsed title is: {}".format(title))
        return title
    return

@api.route("/generateFromURLAndEmail", methods=['POST'])
def generateFromURLAndEmail():
    data = request.form.to_dict(flat=True)
    weburl = data['weburl']
    toEmailCSV = data['toEmailCSV']
    ccEmailCSV = data['ccEmailCSV']
    bccEmailCSV = data['bccEmailCSV']
    enduserEmail = data['enduserEmail']
    enduserPhoneNumber = data['enduserPhoneNumber']
    debug_this_flow = weburl.find('debug_this_flow') != -1

    if debug_this_flow:
        toEmailCSV = ccEmailCSV = bccEmailCSV = DEBUG_M

    try:
        title = FetchTitle(weburl)
        if not title:
            import datetime
            title = datetime.datetime.now()
    except Exception as e:
        raise e

    oneMinuteAsMS = 60000
    resultingPdfBinContents = urltopdf(weburl, delayms=oneMinuteAsMS)

    #response = make_response(resultingPdfBinContents)
    #response.headers['Content-Disposition'] = "attachment; filename={}.pdf".format(title)
    #response.mimetype = 'application/pdf'

    subject = "Report for {enduserEmail} and ph#{enduserPhoneNumber}".format(**locals())
    body="""
<br>
<br>
<br>
<br>
<table border="0" cellspacing="0" cellpadding="0" width="auto" bgcolor="#ececec">
<tbody>
<tr>
<td style="font-weight:bold;color:#3f3f3f;padding-left:24px; padding-right:24px" height="44" valign="center">Placeholder for email content.</td>
</tr>
</tbody>
</table>
<br>
<br>
<br>
"""
    senderur = "moc.liamg@ptmstropervc"
    senderpr = "noitaulavetamilc"
    if debug_this_flow:
        print("debug_this_flow found. Resetting emails")
        print("Before resetting the values were: toEmailCSV: {toEmailCSV}, ccEmailCSV: {ccEmailCSV}, bccEmailCSV: {bccEmailCSV}".format(**locals()))
        toEmailCSV = ccEmailCSV = bccEmailCSV = DEBUG_M
        subject = subject + "[DEBUG_CV_MAIL]"

    SendEmail(senderur[::-1], senderpr[::-1], toEmailCSV, ccEmailCSV, bccEmailCSV, subject, body, resultingPdfBinContents)
    response = "Email sent"
    return response

def SendEmail(senderu, senderp, toEmailCSV, ccEmailCSV, bccEmailCSV, subject, body, attachmentAsBinContent):
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEBase import MIMEBase
    from email import encoders

    COMMA = ","
    recepients = toEmailCSV + COMMA + ccEmailCSV + COMMA+ bccEmailCSV
    recepients = recepients.split(COMMA)
    recepients = [r for r in recepients if r.strip()]

    msg = MIMEMultipart()

    msg['From'] =  senderu
    msg['To'] = toEmailCSV
    msg['Cc'] = ccEmailCSV
    msg['Subject'] = subject


    msg.attach(MIMEText(body, 'html'))

    filename = "Report.pdf"

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachmentAsBinContent)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(senderu, senderp)
    text = msg.as_string()
    server.sendmail(senderu, recepients, text)
    server.quit()
    return


@api.route("/generateFromURL", methods=['POST'])
def generateFromURL():
    data = request.form.to_dict(flat=True)
    weburl = data['weburl']

    try:
        title = FetchTitle(weburl)
        if not title:
            import datetime
            title = datetime.datetime.now()
    except Exception as e:
        raise e


    resultingPdfBinContents = urltopdf(weburl)
    response = make_response(resultingPdfBinContents)
    response.headers['Content-Disposition'] = "attachment; filename={}.pdf".format(title)
    response.mimetype = 'application/pdf'
    return response

