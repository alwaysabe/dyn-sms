import web, sys
sys.path.append('./db')
import model
sys.path.append('./models')
import smspost

urls = (
    '/', 'Index',
    '/login', 'Login',
    '/logout', 'Logout',
    '/home','Home',
    '/upload','Upload',
    '/done','Done',
    '/report','Report'
)

web.config.debug = False
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'))
render = web.template.render('templates', globals={'context': session})


class Index:
    def GET(self):
        if session.get('logged_in', False):
            return render.login()
        session.username = 'Nobody'
	print session
        return render.login()

class Logout:
    def GET(self):
        session.logged_in = False
        session.username = session.username + " => Nobody" 
	session.kill()
	print session
        raise web.seeother('/')

class Login:
    def GET(self):
        print session
	if session.get('logged_in', False):
	    return web.seeother('/home')
        raise web.seeother('/')
    def POST(self):
        login = web.input()
        if model.authenticate(login.username,login.password)=='True':
            session.logged_in = True
            session.username = login.username
            print session
            raise web.seeother('/home')
        else:
          raise web.seeother('/login')

        return render.form()

class Upload:
    def GET(self):
	if session.get('logged_in', False):
	    web.header("Content-Type","text/html; charset=utf-8")
            return render.upload()
	raise web.seeother('/')
    def POST(self):
        x = web.input(myfile={})
        details = web.input()
        filedir = '/home/mobme/web_ses/uploads' # change this to the directory you want to store the file in.
        if 'myfile' in x: # to check if the file-object is created
            filepath=x.myfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
        postfrom = '%s %s' % (details.postfromdate, details.postfromtime)
        postto = '%s %s' % (details.posttodate, details.posttotime)
        smspost.post(details.senderid, details.verbiage, filename, postfrom, postto)
        raise web.seeother('/done')

class Done:
    def GET(self):
	if session.get('logged_in', False):
            return render.done()
	raise web.seeother('/')
    def POST(self):
        return render.done()

class Home:
    def GET(self):
	if session.get('logged_in',False):
	    print session
            return render.home()
	raise web.seeother('/')
    def POST(self):
        return render.home()

class Report:
    def GET(self):
        if session.get('logged_in',False):
            print session
            return render.report()
        raise web.seeother('/')
    def POST(self):
        dates = web.input()
        smsfrom = dates.fromdate
        result = model.getReport(smsfrom)
        return render.showreport(smsfrom,result)

if __name__ == '__main__':
    app.run()
