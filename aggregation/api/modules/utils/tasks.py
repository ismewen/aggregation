import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aggregation import settings
from celery_app import celery


def get_smtp_server():
    if settings.SMTP_TLS:
        smtp_server = smtplib.SMTP_SSL(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,

        )
    else:
        smtp_server = smtplib.SMTP(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
        )
        if settings.SMTP_STARTTLS:
            smtp_server.starttls()
    return smtp_server


@celery.task(bind=True)
def send_email(self, to_list, sub, content):
    """
    发生邮件
    :param to_list: 收件人list
    :param sub: 主题
    :param content: 内容
    :return:
    """
    if not settings.SMTP_ENABLED:
        return False
    email_user = settings.SMTP_USER
    email_password = settings.SMTP_PASS

    msg = MIMEText(content, _subtype='plain', _charset='gb2312')
    msg['Subject'] = sub
    msg['From'] = 'Clouster <%s>' % email_user
    msg['To'] = ";".join(to_list)
    try:
        # smtp_server.connect(smtp_server)
        smtp_server = get_smtp_server()
        smtp_server.login(email_user, email_password)
        smtp_server.sendmail(email_user, to_list, msg.as_string())
        smtp_server.close()
        return True
    except Exception as e:
        print(str(e))
        raise self.retry(exc=e, max_retries=5)


@celery.task(bind=True)
def send_html_email(self, to_list, sub, html, attachments=None):
    """
    发生邮件
    :param to_list: 收件人list
    :param sub: 主题
    :param html: 内容
    :param attachments: 附件
    :return:
    """
    if not settings.SMTP_ENABLED:
        return False

    email_user = settings.SMTP_USER
    email_password = settings.SMTP_PASS

    msg = MIMEMultipart('alternative')
    msg['Subject'] = sub
    msg['From'] = 'AIDE <%s>' % email_user
    msg['To'] = ";".join(to_list)
    try:
        smtp_server = get_smtp_server()
        smtp_server.login(email_user, email_password)

        msg.attach(MIMEText(html, 'html', _charset='utf-8'))
        for attachment in (attachments or []):
            print("attachment", attachment)
            path = attachment.get('url')
            print("path", path)
            part = path.split(":")[0]
            if part in ["http", "https"]:
                import urllib2
                filename = urllib2.unquote(path).decode('utf8').split('/')[-1]
                suffix = filename.split('.')[-1].lower()
                suffix = suffix.split('?')[0]
                if suffix in ["png", "jpeg", "jpg", "bmp", "gif"]:
                    attach = MIMEImage(urllib2.urlopen(path).read(), 'rb')
                else:
                    attach = MIMEText(urllib2.urlopen(path).read(), 'rb')
            else:
                filename = os.path.basename(path)
                suffix = filename.split('.')[-1].lower()
                if suffix in ["png", "jpeg", "jpg", "bmp", "gif"]:
                    attach = MIMEImage(open(path).read(), 'rb')
                else:
                    attach = MIMEText(open(path).read(), 'rb')
            attach["Content-Type"] = 'application/octet-stream'
            attach["Content-Disposition"] = 'attachment; filename=' + attachment.get('filename')
            msg.attach(attach)
        smtp_server.sendmail(email_user, to_list, msg.as_string())
        smtp_server.close()
        print('send email to %s, subject %s' % (msg['To'], msg['Subject']))
        return True
    except Exception as e:
        print(e)
        raise self.retry(exc=e, max_retries=5)
