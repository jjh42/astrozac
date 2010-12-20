"""Code for dealing with log files."""
import models


def parse(logfile):
    """Using the raw text of a model.Log entity, file in the remaining fields (and return the number of images expected."""
    #interpret = json.loads(logfile.raw)
    logging.info('Parsed logfile found ', interpret)
    return interpret['nfiles']

