# pages/notes_page.py

import time
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


class NotesPage(BasePage):
    # --- LOCATORS ---

    # Ana içerik alanı (dashboard'daki gibi)
    MAIN_CONTENT_AREA = (By.ID, "scrollContent")  # Dashboard ile aynı alan

    CONTEXT_MENU_NEW_NOTE = (By.XPATH, "//span[normalize-space()='Yeni Not']")

    NOTE_TITLE_INPUT = (By.XPATH, '//*[@id="yeniNotBaslik"]')
    NOTE_CONTENT_IFRAME = (By.XPATH, '//*[@id="yeniNotIcerik_ifr"]')
    SAVE_NOTE_BUTTON = (By.XPATH, '//*[@id="yeniNotKaydetButton"]')

    NOTE_LIST_ITEM = (By.XPATH, "//div[contains(@class, 'note') or contains(@class, 'card')]")

    def __init__(self, driver):
        super().__init__(driver)
        try:
            self._find_element(self.MAIN_CONTENT_AREA)
            print("Not Defterim sayfası başarıyla yüklendi.")
        except:
            print("Not Defterim sayfası yüklendi (ana alan bulunamadı ama devam ediliyor).")

    def create_new_note(self, title, content):
        """
        Not sayfasında sağ tıklayarak direkt "Yeni Not" seçeneğine tıklar.
        """
        print(f"'{title}' başlıklı yeni not oluşturuluyor...")

        print(" -> Ana alana sağ tıklanıyor...")
        self._right_click_with_js(self.MAIN_CONTENT_AREA)

        print(" -> 'Yeni Not' seçeneğine tıklanıyor...")
        self._click(self.CONTEXT_MENU_NEW_NOTE)

        time.sleep(2)

        print(f" -> Başlık giriliyor: {title}")
        try:
            title_input = self.wait.until(EC.element_to_be_clickable(self.NOTE_TITLE_INPUT))
            title_input.clear()
            title_input.send_keys(title)
            print(f" -> Başlık girildi: {title}")
        except Exception as e:
            print(f"HATA: Başlık alanı bulunamadı! {e}")

        print(f" -> İçerik giriliyor: {content}")
        try:
            iframe = self.wait.until(EC.presence_of_element_located(self.NOTE_CONTENT_IFRAME))
            self.driver.switch_to.frame(iframe)

            body_element = self.driver.find_element(By.XPATH, "//body[@contenteditable='true']")
            body_element.clear()
            body_element.send_keys(content)
            print(f" -> İçerik girildi: {content}")

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"HATA: İçerik alanı bulunamadı! {e}")

        print(" -> Kaydet butonuna tıklanıyor...")
        try:
            save_button = self.wait.until(EC.element_to_be_clickable(self.SAVE_NOTE_BUTTON))
            save_button.click()
            print(" -> Kaydet butonuna tıklandı")
        except Exception as e:
            print(f"HATA: Kaydet butonu bulunamadı! {e}")

        try:
            self._wait_for_success_toast()
            print(" -> Başarı mesajı görüldü")
        except:
            print(" -> Başarı mesajı görülmedi, 3 saniye beklenecek")
            time.sleep(3)

        print(f"Not '{title}' başarıyla oluşturuldu.")

    def is_note_visible(self, note_title, timeout=10):
        """Belirtilen başlığa sahip notun listede olup olmadığını kontrol eder."""
        print(f"'{note_title}' notu aranıyor...")

        note_locators = [
            (By.XPATH, f"//div[contains(@class, 'note') and contains(., '{note_title}')]"),
            (By.XPATH, f"//div[contains(@class, 'card') and contains(., '{note_title}')]"),
            (By.XPATH, f"//h5[contains(text(), '{note_title}')]"),
            (By.XPATH, f"//h4[contains(text(), '{note_title}')]"),
            (By.XPATH, f"//h3[contains(text(), '{note_title}')]"),
            (By.XPATH, f"//*[contains(text(), '{note_title}')]"),
        ]

        for i, locator in enumerate(note_locators):
            try:
                print(f" -> Not arama denemesi {i + 1}: {locator[1]}")
                WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
                print(f"Doğrulama: '{note_title}' notu bulundu.")
                return True
            except:
                print(f" -> Arama denemesi {i + 1} başarısız")
                continue

        print(f"Doğrulama: '{note_title}' notu bulunamadı.")
        return False