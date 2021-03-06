import csv, os, MySQLdb, datetime, time, traceback,sys
path = '/home/mobme/web_ses/uploads/'
dbcursor = None

now = datetime.datetime.now()

settings = {'host': 'localhost',
            'port': 5041,
            'user': 'smsc',
            'password': 'smsc',
            'posttosmsc': 0,
            'mode': '',
            'priority': '100',
            'iprefix': '00',
            'postfrom': now.strftime('%Y-%m-%d 08:00:00'),
            'postto': now.strftime('%Y-%m-%d 20:00:00'),
            'timeofdaybegin': '08:00:00',
            'timeofdayend': '20:00:00',
            }


def connect_mysql():
    global dbcursor
    if not dbcursor:
        d = MySQLdb.connect(db='smsc', user='smsc', passwd='smsc', use_unicode=True)
        dbcursor = d.cursor()
        dbcursor.execute('set autocommit=false')

def db_exec(*a):
    for retry in range(100):
        try:
            dbcursor.execute(*a)
            break
        except MySQLdb.OperationalError, e:
            if e.args[0] == 2006: # server has gone away
                time.sleep(5)
                connect_mysql()
            else:
                break

def normalizenumber(defaultarea, n):
    if n.startswith('+'):
        return settings.get('iprefix') + n[1:]
    if n.startswith('00'):
        return settings.get('iprefix') + n[2:]
    if n.isdigit():
        return settings.get('iprefix') + defaultarea + n
    return n

def senddb(settings, numberlist):
  try: 
    global defaultarea
    sender = settings.get('sender')
    text = settings.get('text')
    priority = settings.get('priority')
    mode = settings.get('mode')
    for ch in text:
        if ord(ch) > 255:
            mode += append(',ucs2')
            break
  except Exception, e:
    print 'Error 1: ',e
    for tb in traceback.format_tb(sys.exc_info()[2]):
      print tb

  try:
    db_exec('select area from status')
    defaultarea = str(dbcursor.fetchone()[0])
    defaultarea = '91'
    db_exec('select receiver from dnd')
    dnd = dict([(k[0], None) for k in dbcursor.fetchall()])

    numberlist = [normalizenumber(defaultarea, n) for n in numberlist]
    numberlist = [n for n in numberlist if not dnd.has_key(n)]
  except Exception,e:
    print 'Error 2: ',e
    for tb in traceback.format_tb(sys.exc_info()[2]):
      print tb
  try:
    db_exec('insert into batch (postfrom, postto, timeofdaybegin, timeofdayend, sender, mode, text, priority, count) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (settings.get('postfrom'), settings.get('postto'), settings.get('timeofdaybegin'), settings.get('timeofdayend'), sender, mode, text, priority, len(numberlist)))
    batchid = dbcursor.lastrowid
    if settings.get('printbatchid'):
        print 'batchid', batchid
    for number in numberlist:
        db_exec('insert into sms (batchid, queue, receiver, createtime) values(%s,%s,%s,now())', (batchid, 'user', number))
        print 'posted', number
    db_exec('commit')
  except Exception,e:
    print 'Error3: ',e
    for tb in traceback.format_tb(sys.exc_info()[2]):
      print tb
def get_verbiage(data,field,header):
    for i in xrange(len(header)):
       data = data.replace("<"+header[i]+">",field[i])
    return data

def post(senderid, text, file, postfrom, postto):
    global settings
    connect_mysql()
    filename = path+file
    upload = csv.reader(open(filename,"rb"))
    header = upload.next()
    total_fields= len(header)
    for fields in upload:
        verbiage = get_verbiage(text,fields, header)
        msisdn = fields[header.index('msisdn')]
	settings.update({'sender':senderid})
        settings.update({'text':verbiage})
        settings.update({'priority':'100'})
        settings.update({'mode':'10'})
        settings.update({'postfrom':postfrom})
        settings.update({'postto':postto})
        settings.update({'receiver':msisdn})
#        settings['text'] = verbiage
#	settings['priority'] = '50'
#	settings['mode'] = '10'
#	settings['printbatchid'] = 'True'
#	settings['receiver'] = msisdn
	print settings
        if isinstance([msisdn][0], str) and len([msisdn][0])==10:
            print 'send db'
            try:
                senddb(settings, [msisdn])
            except Exception, e:
                print 'ERROR: ', e
		for tb in traceback.format_tb(sys.exc_info()[2]):
		    print tb

##        senddb(settings, [msisdn])

def send_sms(senderid, verbiage, msisdn):
    cmd = "/usr/local/ss7/sbin/smscpost --sender %s --receiver %s --text '%s'" % (senderid, msisdn, verbiage)
#    os.system(cmd)
#    print cmd

#post("abe","hello <value1>, please recharge with rs.<value2>","delhi.csv")
