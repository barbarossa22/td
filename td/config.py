"""
.. module:: config
   :platform: Unix
   :synopsis: Config scanner for td app's ini files.

.. moduleauthor:: Mykola Radionov <moodaq@gmail.com>


"""
from ConfigParser import SafeConfigParser


class ConfigScanner:
    def __init__(self, config_location):
        self.config_location = config_location

    def parse_section(self, section_name):
        """Get dict of params for each unique key in the section.

        [('mysql.user', 'root'), ('mysql.password', '1234'),
         ('postgres.host', 'localhost')] ->
         {'mysql': {'user': 'root', 'password': '1234'},
          'postgres': {'host': 'localhost'}}

        :param section_name:
        :type: str.
        :return: dictionary with params for each unique key.
        :rtype: dict.
        """
        parser = SafeConfigParser()
        parser.read(self.config_location)
        section_items = dict(parser.items(section_name))

        result = {}

        for key in section_items.keys():
            prefix, true_key = key.split('.')
            result.setdefault(prefix, {})
            result[prefix][true_key] = section_items.get(key)

        return result

    def get_subsection_in_section(self, subsection_name, section_name):
        """ Get dict of params for one single key (subsection) in the section.

        :param subsection_name:
        :type: str.
        :param section_name:
        :type: str.
        :return: dictionary with items for single unique key in section.
        :rtype: dict.
        """
        section = self.parse_section(section_name)
        return section.get(subsection_name)


    #second method for db:
    #def get_engine_creds(self, engine):
    #   raise error if engine isn't proper
    #   self.parse_section('databases').get(engine)
    # is it hardcoded?