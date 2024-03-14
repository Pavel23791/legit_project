import sys
import pytest
import yaml
import time
import os
from playwright.sync_api import sync_playwright

current_script_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_script_path)

# Parameters for the tests: {'mail': True(valid), False(not valid)}
test_values = {'noatmail@test': False, 'notamail': False, 'notamail@': False, 'noatmail@test': False, 'amail@test.com': True}

class Test_legit_log_on_screen():
    '''
    Test the mail in the logon screen
    Run 4 different mails - verify only the valid mail passed: amail@test.com
    '''
    
    @classmethod
    def setup_class(self):
        '''
        Setup the class with needed parameters
        '''
        # # Open the yaml configuration file
        with open(os.path.join(current_script_dir, 'legit_test_yaml.yaml'), 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                pytest.exit("Failed to get configuration file", returncode=3)

        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(channel='chrome', headless=False)  # Set headless=False to see the browser UI
        self.page = self.browser.new_page()
    
    @pytest.mark.parametrize('test_mail', test_values)
    def test__legit_log_on(self,test_mail):
        '''
        The test flow every assert is a step.
        '''
        assert self.connect_to_the_site(test_mail), print("Failed to connect to the website")

    def connect_to_the_site(self, mail):
        '''
        func to connect to the site using the givven mail
        return True if not try to connect when not valid mail or try to connect when valid
        False if not
        '''
        self.page.goto(self.config['web_link'])
        self.page.wait_for_load_state('load')
        self.page.locator('input[name="username"]').fill(mail)
        self.page.locator('input[name="password"]').type('wrongpass', delay=50)
        self.page.get_by_role('button', name='Sign in').click()
        time.sleep(5)
        error_alert = self.page.locator('.amplify-alert--error')
        if error_alert.count() > 0 and test_values[mail] == False:
            print(f"There was a not valid mail input but still tried to connect.")
            self.page.screenshot(path=f'connect_to_the_site_{mail}.jpg', full_page=True)
            return False
        
        return True
            
    @classmethod
    def teardown_class(self):
        '''
        When test is over close the web browser.
        '''
        self.browser.close()

    if __name__ == "__main__":
        exit_code = pytest.main(['-v','--cache-clear', "--disable-pytest-warnings", current_script_path])  # full execution
        print("Tests Exit code: " + str(exit_code))
        sys.exit(exit_code)
        # Exit code 0:All tests were collected and passed successfully
        # Exit code 1:Tests were collected and run but some of the tests failed
        # Exit code 2:Test execution was interrupted by the user
        # Exit code 3:Internal error happened while executing teststs
        # Exit code 4:pytest command line usage error
        # Exit code 5:No tests were collected
        