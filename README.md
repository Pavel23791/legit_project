# legit_project
Files description:
1. ReadMe.md - current file.
2. conftest.py - set commandline variables to pass to the test.
3. connect_to_the_site_noatmail@test.jpg - screenshot for the bug.
4. legit_project.py - main test of the exersice.
5. legit_test_yaml.yaml - configuration file for the tests.
6. mail_user_test.py - A test flow to find the bug.
7. requirements.txt - the reuired pip modules for the tests.

Manual Run:
1. Install python on your machine.
2. Download all the files to a local directory.
3. install requirments.txt:
pip install -r requirements.txt
4. Run the test:
   pytest -v <PATH_TO_legit_project.py> --username <Valid_username> --password <valid_password>


Second test: mail_user_test.py
1. No need to add any parameters: pytest -v <PATH_TO_legit_mail_user_test.py>
2. This test will trigger a bug.
3. The bug described in "issues".
