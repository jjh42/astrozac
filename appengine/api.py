from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import deferred
import os
import logging
import cas
import models
import logfiles


def create_file_entry_from_blobinfo(blobinfo):
    """Create an entry in the file database for the blob given as a blobinfo object."""
    filedb = models.File(owner=users.get_current_user(), blob=blobinfo.key(),
                mimetype=blobinfo.content_type, filename=blobinfo.filename,
                filesize=blobinfo.size)
    filedb.put()
    return filedb

class UploadHandler(blobstore_handlers.
                    BlobstoreUploadHandler):
    def post(self):
        uploaded_files = self.get_uploads('files') 
        logging.info('Handling upload of %d files' % len(uploaded_files))
        uploaded_files = cas.dedup(uploaded_files) # Remove any duplicate blobs
        # Create corresponding database entries for these blobs.
        files = [create_file_entry_from_blobinfo(f) for f in uploaded_files] 
        deferred.defer(process_uploads, [f.key() for f in files])
        self.redirect('/')

def process_uploads(new_entries):
    """Process the newly uploaded entries which are given as a list of keys in new_entries."""
    logging.info("Processes %d entries" % len(new_entries))

application = webapp.WSGIApplication(
                                     [('/api/handleupload', UploadHandler)],
                                     debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
