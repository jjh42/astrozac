from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import blobstore_handlers
import os
import logging
import cas
import models
import logfiles


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file') 
        logging.info('Handling upload of %d files' % len(upload_files))
        upload_files = cas.dedup(upload_files) # Remove any duplicate blobs
        self.redirect('/')
         
application = webapp.WSGIApplication(
                                     [('/api/handleupload', UploadHandler)],
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
