'''
Template Component main class.

'''
import csv
import logging
from datetime import datetime
from pathlib import Path

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException
from keboola.component import CommonInterface
from keboola.component import dao

ci = CommonInterface

# configuration variables
KEY_API_TOKEN = '#api_token'
# KEY_PRINT_HELLO = 'print_hello'
KEY_PRINT_ROWS = 'print_rows'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_PRINT_ROWS]
REQUIRED_IMAGE_PARS = []

class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        '''
        Main execution code
        '''
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        params = self.configuration.parameters

        input_tables=self.get_input_tables_definitions()
        first_table=input_tables[0]
        SOURCE_FILE_PATH=first_table.full_path
        logging.info(SOURCE_FILE_PATH)
        
        RESULT_FILE_PATH2=Path(self.tables_out_path)
        new_file=RESULT_FILE_PATH2.joinpath('output.csv')
        logging.info(new_file)  

        # RESULT_FILE_PATH = self.create_out_table_definition('output2.csv', incremental=True, primary_key=['timestamp'])
        table_def = self.create_out_table_definition(name='output.csv'
                        , incremental = True
                        , primary_key=['row_number']
                        )

        
        # DO whatever and save into out_table_path
        with open(SOURCE_FILE_PATH, 'r') as input, open(new_file, 'w+', newline='') as out:
            reader = csv.DictReader(input)
            new_columns = reader.fieldnames
            # append row number col
            new_columns.append('row_number')
            writer = csv.DictWriter(out, fieldnames=new_columns, lineterminator='\n', delimiter=',')
            writer.writeheader()
            for index, l in enumerate(reader):
                # print line
                if KEY_PRINT_ROWS:
                    print(f'Printing line {index}: {l}')
                # add row number
                l['row_number'] = index
                writer.writerow(l)
        

        if params.get(KEY_PRINT_ROWS):
            logging.info("Print rows")

        # get last state data/in/state.json from previous run
        previous_state = self.get_state_file()
        logging.info(previous_state.get('last_update'))

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(table_def)
        
        # Write new state - will be available next run
        self.write_state_file({"last_update": datetime.now().isoformat()})


if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
