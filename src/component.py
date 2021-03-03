'''
Template Component main class.

'''
import logging
import os
import sys
from pathlib import Path

from keboola.component import CommonInterface

# configuration variables
KEY_API_TOKEN = '#api_token'
KEY_PRINT_HELLO = 'print_hello'

# #### Keep for debug
KEY_DEBUG = 'debug'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = []
REQUIRED_IMAGE_PARS = []

APP_VERSION = '0.0.1'


class Component(CommonInterface):
    def __init__(self, debug=False):
        # for easier local project setup
        if not os.environ.get('KBC_DATADIR'):
            data_folder_path = Path(__file__).resolve()\
                .parent.parent.joinpath('data').as_posix()
            super().__init__(data_folder_path=data_folder_path)
        else:
            super().__init__()

        # override debug from config
        if self.configuration.parameters[KEY_DEBUG]:
            debug = True
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.info('Running version %s', APP_VERSION)
            logging.info('Loading configuration...')

        try:
            # validation of required parameters. Produces ValueError
            self.validate_configuration(REQUIRED_PARAMETERS)
            self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        except ValueError as e:
            logging.exception(e)
            exit(1)

    def run(self):
        '''
        Main execution code
        '''
        params = self.configuration.parameters

        # ####### EXAMPLE TO REMOVE
        if params.get(KEY_PRINT_HELLO):
            logging.info("Hello World")

        # ####### EXAMPLE TO REMOVE END


"""
        Main entrypoint
"""
if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_arg = sys.argv[1]
    else:
        debug_arg = False
    try:
        comp = Component(debug_arg)
        comp.run()
    except Exception as exc:
        logging.exception(exc)
        exit(1)
