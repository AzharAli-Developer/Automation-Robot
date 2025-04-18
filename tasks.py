import os
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Browser.Selenium import Selenium
import time
from RPA.PDF import PDF
from RPA.Archive import Archive


class Bot:

    """Done login and signup using credentials and take screenshot of the robot and the reception and then merge
    in one PDF file. """

    def __init__(self):
        self.browser = Selenium()
        self.pdf = PDF()

    def open_order_website(self):
        self.browser.open_available_browser("https://robotsparebinindustries.com/#/robot-order")
        time.sleep(1)

    def close_modal(self):
        self.browser.click_button('//div[@class="alert-buttons"]/button[@class="btn btn-dark"]')

    def download_order_file(self):
        http= HTTP()
        download_path = os.path.join(os.getcwd(), 'output')
        http.download(url='https://robotsparebinindustries.com/orders.csv',target_file= download_path, overwrite=True)

    def get_orders(self):
        table = Tables()
        csv_file_path = os.path.join(os.getcwd(), 'output', 'orders.csv')
        data = table.read_table_from_csv(csv_file_path)
        return data

    def fill_the_form(self, data):
        self.browser.select_from_list_by_value('//select[@id="head"]', data["Head"])
        self.browser.find_element(f'//div[@class="stacked"]//label[@for="id-body-{data["Body"]}"]').click()
        self.browser.input_text('//input[@type="number"]', data["Legs"])
        self.browser.input_text('//input[@id="address"]', str(data['Address']))
        self.browser.scroll_element_into_view('//button[@id="order"]')
        self.browser.click_button('//button[@id="order"]')

        while self.browser.does_page_contain_element('//div[@class="alert alert-danger"]'):
            self.browser.scroll_element_into_view('//button[@id="order"]')
            self.browser.click_button('//button[@id="order"]')

        self.browser.wait_until_element_is_visible('//button[@id="order-another"]', timeout=30)

        self.order_reciept_pdf(data['Order number'])
        self.robot_screenshot(data['Order number'])
        time.sleep(2)
        self.embed_robot_to_pdf(data['Order number'])
        self.browser.click_button('//button[@id="order-another"]')
        self.close_modal()

    def order_reciept_pdf(self,name):
        receipt_results = self.browser.find_element('//div[@id="receipt"]')
        html_content = receipt_results .get_attribute('innerHTML')
        pdf_file_path = os.path.join(os.getcwd(), f"output/Receipt/Receipt{name}.pdf")
        self.pdf.html_to_pdf(html_content, pdf_file_path)

    def robot_screenshot(self,name):
        robot_file_path = os.path.join(os.getcwd(), f"output/screenshoot/robot{name}.png")
        self.browser.capture_element_screenshot('//div[@id="robot-preview-image"]',filename=robot_file_path)

    def embed_robot_to_pdf(self, name):
        pdf_path = os.path.join(os.getcwd(), f'output/Receipt/Receipt{name}.pdf')
        image_path = os.path.join(os.getcwd(), f"output/screenshoot/robot{name}.png")
        self.pdf.add_files_to_pdf(files=[pdf_path,image_path], target_document=pdf_path)

    def zip_receipts(self):
        arc = Archive()
        folder_path= os.path.join(os.getcwd(), 'output/Receipt')
        zip_path= os.path.join(os.getcwd(), 'output/Receipt.zip')
        arc.archive_folder_with_zip(folder_path, zip_path)


bot = Bot()
bot.open_order_website()
bot.close_modal()
bot.download_order_file()
orders = bot.get_orders()
for row in orders:
    bot.fill_the_form(row)
bot.zip_receipts()
