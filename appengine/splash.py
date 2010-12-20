from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os

class SplashPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            # User is already logged in so redirect to the main page.
            self.redirect('/main')
        else:
            template_values = {'login_url' : users.create_login_url('/')}
            path = os.path.join(os.path.dirname(__file__), 'templates/splash.html')
            self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/splash', SplashPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


