import yagmail

yag = yagmail.SMTP('zhuiluoxingcheng@gmail.com', '122979088wen')

to = 'ismewen@163.com'
subject = 'This is obviously the subject'
body = 'This is obviously the body'
html = '<a href="https://pypi.python.org/pypi/sky/">Click me!</a>'
img = '/local/file/bunny.png'

yag.send(to=to, subject=subject, contents=body)
