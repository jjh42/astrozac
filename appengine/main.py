from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
import os
import logging

import models

class WithUserPage(webapp.RequestHandler):
    """Class shared by all pages rendered while we have a user logged in."""
    def render_template(self,templatename, values={}):
        """Render a django template (assumes it's found in templates/) and include
        values that are needed for every page."""
        default_values = {
            'nickname': users.get_current_user().nickname(),
            'logout_url' : users.create_logout_url('/'),
            }
        default_values.update(values)
        path = os.path.join(os.path.dirname(__file__), 'templates/%s' % templatename)
        self.response.out.write(template.render(path, default_values))

    def get_current_user_entity(self):
        """Returns the database entry for the currently logged in the user."""
        return db.Query(models.User).filter('user', users.get_current_user()).get() or models.User(user=users.get_current_user())

class MainPage(WithUserPage):
    def get(self):
        self.render_template('main.html',
                             {'upload_url': blobstore.create_upload_url('/api/handleupload')})


class SettingsPage(WithUserPage):
    class SettingsForm(djangoforms.ModelForm):
        class Meta:
            model = models.User
            exclude = ['user']
        
    def get(self):
        logging.info('Populating form')
        logging.info(self.get_current_user_entity().initials)
        self.render_template('usersettings.html', {'form' : self.SettingsForm(
            instance=self.get_current_user_entity())})

    def post(self):
        data = self.SettingsForm(self.request.POST, instance=self.get_current_user_entity())
        if data.is_valid():
            logging.info('User updated initials')
            entity = data.save(commit=False)
            logging.info(entity.initials)
            entity.user = users.get_current_user()
            entity.put()
            self.redirect('/')
        else:
            logging.warning('Invalid settings submission.')
            self.renderTemplate('usersettings.html', {'form' : data})


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/settings', SettingsPage)],
                                     debug=True)


class RedirectToLogin(webapp.RequestHandler):
    def get(self):
        self.redirect('/splash')
    
nologin = webapp.WSGIApplication(
        [(r'.*', RedirectToLogin)], debug=True)

    
def main():
    # Start by checking the user is logged in (if not we give redirect to splash page).
    if not users.get_current_user():
        # No users are logged in redirect to splash page.
        logging.info('Redirect user to login page')
        run_wsgi_app(nologin)
    else:    
        logging.info('Serving main page')
        run_wsgi_app(application)

if __name__ == "__main__":
    main()


