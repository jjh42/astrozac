"""Content-addressable storage implemented on top of the Blob store. We used SHA-512 hashes
and assume that content with the same hash is identical. Intentionally made to have an
interface very similar to that of Blob."""

from google.appengine.ext import blobstore
from google.appengine.ext import db
import logging
import hashlib

class ExtBlobInfo(db.Model):
    """Model for storing hashes of blobs."""
    blobhash = db.ByteStringProperty(required=True)
    blobref = blobstore.BlobReferenceProperty(required=True)


def dedup(blobs):
    """Called from inside an upload handler. Given a list of blob handles
    we check if any of the blobs already exist, if so we delete the redundant blob
    and replace the blob with the key to the previous blob.

    We also append a property to the return blobs 'fresh' indicate if the blobs
    already existed.

    An (intentional) side-effect of calling this function is that is records the hash
    of any new blobs for future comparision (in the ExtBlobInfo class)."""
    def _dedup(blob):
        logging.info('Deduplicating blob %s' % blob.key())
        newblobhash = blob_sha512(blob).hexdigest()
        dup = db.Query(ExtBlobInfo).filter('blobhash', newblobhash).get()
        if dup:
            logging.info('Found duplicate blob %s' % dup.blobref.key())
            assert(dup.blobref.size == blob.size)
            blob.delete()
            # Return the blobinfo corresponding to this key
            dupblob = dup.blobref
            dupblob.fresh = False
            return dupblob
        else: # This blob is unique so return the pointer.
            blob.fresh = True
            # Save a copy of this hash
            ExtBlobInfo(blobhash=newblobhash, blobref=blob).put()
            return blob

    return [_dedup(b) for b in blobs]

def blob_sha512(blob):
    """Perform a SHA512 hash on a blob in the blobstore return a hash object."""
    h = hashlib.sha512()
    position = 0
    # Loop indefinitely until all the blob's data has been processed
    while True:
        # Grab the next (or first) 'block' of data from the provided
        # blob
        data = blobstore.fetch_data(blob, position, position +
                                    (blobstore.MAX_BLOB_FETCH_SIZE - 1))
        # Insert the fetched data into the md5 object
        h.update(data)
        # If the length of the provided data is less than the maximum
        # amount of data fetchable by the fetch_data function, there
        # is no more data to fetch.
        if len(data) < blobstore.MAX_BLOB_FETCH_SIZE:
            break
        # Update the position so the block after the one we just
        # processed is used for the next loop
        position += blobstore.MAX_BLOB_FETCH_SIZE
    # Every bit of the blob should now be hashed, return the result of
    # the md5 hashing object
    return h

