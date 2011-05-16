import MySQLdb

def connect():
    return MySQLdb.connect(host="localhost", user="smsc", passwd="smsc", db="smsc")
 

def authenticate(user, password):
    q_users= "select password from user where user='%s'"
    cursor=connect().cursor()
    cursor.execute(q_users % (user))
    rs= cursor.fetchall()
    cursor.close()
    if rs:
        for row in rs:
            if row[0] == password:
                return 'True'
            else: 
                return 'False'
    else:
        return 'False'

def getReport(valid_date):
    rep="select distinct history.state, count(*) from history, batch where batch.mode='10' and batch.seqno=history.batchid and history.createtime like '%s %s'  group by history.state union select distinct sms.state, count(*) from sms, batch where batch.mode='10' and batch.seqno=sms.batchid  and sms.createtime like '%s %s'group by sms.state" % (valid_date,"%", valid_date, '%')
    cur=connect().cursor()
    cur.execute(rep)
    hist= cur.fetchall()
    cur.close()
    states={}
    for state in hist:
        if states.has_key(state[0]):
            states[state[0]]=int(state[1])+states[state[0]]
        else:
            states[state[0]]=int(state[1])

    total=0
    for s in states:
        total+=states[s]
    states.update({'total':total})
    if states.has_key('P'):
        print 'yes'
    else:
        states.update({'P':0})
    if states.has_key('F'):
        print 'yes'
    else:
        states.update({'F':0})
    if states.has_key('total'):
        print 'yes'
    else:
        states.update({'total':0})
    print states
    return states

