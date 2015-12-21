# Base class to inherit from

class Base_Check(object):
    """ Check to inherit from """
    label = "Brief Label for Check"
    description = """ Detailed descripton of the Check """

    def filter(s, keys):
        """ Filter out keys and attributes we're interested in """
        raise NotImplementedError

    def fix(s):
        """ Attempt to fix the issue automatically """
        raise NotImplementedError
