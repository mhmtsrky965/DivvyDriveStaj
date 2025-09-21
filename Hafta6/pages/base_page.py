# pages/base_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)
        self.actions = ActionChains(self.driver)

    def _find_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def _send_keys(self, locator, text):
        element = self._find_element(locator)
        element.clear()
        element.send_keys(text)

    def _right_click_with_js(self, locator, x_offset=5, y_offset=5):
        """
        Bir elementin belirtilen ofset koordinatına JavaScript kullanarak sağ tıklar.
        """
        print(f"JavaScript ile sağ tıklama yapılıyor: {locator}")
        element = self.wait.until(EC.presence_of_element_located(locator))

        script = """
        var element = arguments[0];
        var x = arguments[1];
        var y = arguments[2];
        var rect = element.getBoundingClientRect();
        var rightClickEvent = new MouseEvent('contextmenu', {
            bubbles: true,
            cancelable: false,
            view: window,
            button: 2,
            buttons: 2,
            clientX: rect.left + x,
            clientY: rect.top + y
        });
        element.dispatchEvent(rightClickEvent);
        """
        self.driver.execute_script(script, element, x_offset, y_offset)

    def _click_with_js(self, locator):
        """
        Bir elementi JavaScript ile tıklar.
        """
        print(f"JavaScript ile tıklama yapılıyor: {locator}")
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].click();", element)

    def _right_click_on_element(self, locator):
        """
        Standart ActionChains ile bir elementin tam üzerine sağ tıklar.
        """
        element = self._find_element(locator)
        self.actions.context_click(element).perform()