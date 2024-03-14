import sys
import pytest
import yaml
import time
import re
import os
from playwright.sync_api import sync_playwright

current_script_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_script_path)

class Test_legit_project():
    '''
    1. Navigate to the website and log in with valid credentials.
    2. Add two different products to the shopping cart.
    3. Navigate to the shopping cart and verify that the correct products are added.
    4. Proceed to the checkout page, and fill in the shipping information.
    5. Complete the checkout process and verify that the order is placed successfully on the orders page.
    '''
    
    @classmethod
    def setup_class(self):
        '''
        Setup the class with needed parameters
        '''
        # Open the yaml configuration file
        with open(os.path.join(current_script_dir, 'legit_test_yaml.yaml'), 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                pytest.exit("Failed to get configuration file", returncode=3)
        
        self.complete_message = str() # The message of the order number after it completes.
        self.items_dict = dict() # dict for items ids
        tmp_dict = dict() # temp dict to change the original
        self.products = dict() # dict for product number and the cost

        for item in self.config['products_to_change'].keys():
            self.items_dict[f'#product_id_{item}-product-quantity-select'] = self.config['products_to_change'][item]
            tmp_dict[f'Product {item}'] = self.config['products_to_change'][item]
        
        self.config['products_to_change'] = tmp_dict
        for item in self.config['products_to_change'].keys():
            self.products[item] = ''
        

        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(channel='chrome', headless=False)  # Set headless=False to see the browser UI
        self.page = self.browser.new_page()

    def test__legit_project(self, username, password):
        '''
        The test flow every assert is a step.
        '''
        assert self.connect_to_the_site(username, password), print("Failed to connect to the website")
        assert self.change_and_add_to_cart(), print("Failed change order amount and add it to cart")
        assert self.verify_shopping_cart(), print("Failed to verify the shopping cart")
        assert self.proceed_to_checkout(), print("Failed to perform checkout")
        assert self.verify_order(), print("Failed to verify the order")

        

    def connect_to_the_site(self, username, password):
        '''
        func to connect to the site using the cred from command line
        return True if connected
        False if not
        '''
        try:
            self.page.goto(self.config['web_link'])
            self.page.wait_for_load_state('load')
            self.page.locator('input[name="username"]').fill(username)
            self.page.locator('input[name="password"]').type(password, delay=50)
            self.page.get_by_role('button', name='Sign in').click()
            
            # Wait for the page to load with a timeout of 10 seconds
            try:
                self.page.wait_for_selector('text=Online Shopping Website', timeout=10000)
                print("Page loaded successfully.")
                self.page.screenshot(path='connect_to_the_site_success.jpg', full_page=True)
                return True
            except:
                print("Failed to load the page.")
                self.page.screenshot(path='connect_to_the_site_fail_load.jpg', full_page=True)
                return False
            
        except Exception as ex:
            print(f"Failed to connect to the site with exception {ex}")
            self.page.screenshot(path='connect_to_the_site_error.jpg', full_page=True)
            return False
        
    def change_and_add_to_cart(self):
        '''
        Choose and change the amount of items in 2 products (depends on the yaml file)
        return True if values changed and checked successfully
        False if not 
        '''
        all_items_changed_and_added = True
        
        for item in self.items_dict.keys():        
            try:
                self.page.select_option(item, value=str(self.items_dict[item]))
            except Exception as ex:
                print(f"Failed to change {item} to {self.items_dict[item]} with exception: {ex}")
                self.page.screenshot(path='change_and_add_to_cart_two_FAIL.jpg', full_page=True)
                return False
            
            selected_value = self.page.locator(item).evaluate("element => element.value")
            if selected_value != self.items_dict[item]:
                print(f"The selected item is {selected_value} but suppose to be {self.items_dict[item]}")
                self.page.screenshot(path=f'change_and_add_to_cart_Wrong_item_{item}.jpg', full_page=True)
                all_items_changed_and_added = False
            else:
                print(f"The selected item is good")
        
        for product_num in self.products.keys():
            try:
                self.page.locator(f'li:has-text("{product_num}") >> button').click()
                item_cost = self.page.locator(f'li:has-text("{product_num}")').text_content()
                self.products[product_num] = re.search(r'\$\d+(?:\.\d+)?', item_cost).group()
                # self.page.wait_for_selector('text=Shopping Cart', timeout=10000)
            
            except Exception as ex:
                print(f"Failed to click on Add to cart button with exception: {ex}")
                self.page.screenshot(path=f'change_and_add_to_cart_Click_{item}.jpg', full_page=True)
                all_items_changed_and_added = False

        return all_items_changed_and_added
    
    def verify_shopping_cart(self):
        '''
        Verify all wanted items are in the shopping cart
        True if they are
        False if not
        '''
        try:
            self.page.get_by_role('link', name='Shopping Cart').click()
        except Exception as ex:
            print(f"No shoping cart button located, an exception happened: {ex}")
            self.page.screenshot(path=f'verify_shopping_cart_click_on_shopping_cart', full_page=True)
            return False
        
        all_products_located = True
        for product in self.products.keys():
            if self.page.locator(f'li:has-text("{product}")').is_visible() == False:
                print(f"The product {product} not located.")
                all_products_located = False
            
            else:
                product_text = self.page.locator(f'li:has-text("{product}")').text_content()
                product_quantity = re.search(r'\(Quantity: \d+\)', product_text).group()
                product_cost = re.search(r'\$\d+(?:\.\d+)?', product_text).group()

                # Check product cost
                if not self.products[product] in product_cost:
                    print(f"The product is {product_cost} cost but should be{self.products[product]}.")
                    all_products_located = False

                # Check product quantity
                if not self.config['products_to_change'][product] in product_quantity:
                    print(f"The quantity is {product_quantity} but should be{self.config['products_to_change'][product]}.")
                    all_products_located = False

        if all_products_located:
            try:
                self.page.get_by_role('button', name='Proceed to Checkout').click()
            except Exception as ex:
                print("Failed to click on 'Proceed to Checkout'.")
                return False

        return True
    
    def proceed_to_checkout(self):
        '''
        enter the address from the configuration file
        click on complete checkout
        wait for a popupmessage with order number to appear than save the order number
        return True if all success
        False if not
        '''
        try:
            self.page.fill('#shipping-address-text', self.config['shipping_address'])
        except Exception as ex:
            print(f"Failed to input shippment text with exception: {ex}")
            return False
        
        try:
            self.page.on('dialog', self.handle_dialog)
            self.page.get_by_role('button', name='Complete Checkout').click()
            self.page.wait_for_timeout(10000)
            
            if self.complete_message == '':
                print("Failed to extract the order number message.")
                return False
            else:
                print(f"Order number is: {self.complete_message}")
                return True

        except Exception as ex:
            print(f"Failed to complete checkout with exception: {ex}")
            return False
    
    def verify_order(self):
        '''
        Verify the order number is in the orders page
        True if it is
        False if not
        '''
        try:
            self.page.get_by_role('link', name='Orders').click()
            time.sleep(5)
        except Exception as ex:
            print(f"No Orders button located, an exception happened: {ex}")
            self.page.screenshot(path=f'verify_order_FAIL_click_on_Orders', full_page=True)
            return False
        
        order_found = False
        divs = self.page.locator('div').all()
        for div in divs:
            if div.text_content().startswith(f'Order {self.complete_message}'):
                order_found = True

        if order_found:
            print("Found the order - flow completed")
            return True
        else:
            print(f"No order number: {self.complete_message}")
            return False

    def handle_dialog(self, dialog):
        '''
        catch the popup message for the order number.
        '''
        prefix = 'checkout complete: '
        if dialog.message.startswith(prefix):
            self.complete_message = dialog.message[len(prefix):]
        dialog.accept()

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
        