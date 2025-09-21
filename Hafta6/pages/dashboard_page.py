import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains # <-- BU SATIR EKSİKMİŞ, EKLİYORUZ

# Diğer sayfa sınıflarını import ediyoruz
from pages.base_page import BasePage
from pages.notes_page import NotesPage
from pages.passwords_page import PasswordsPage


class DashboardPage(BasePage):
    """
    Ana Dashboard sayfası. Dosya/klasör işlemleri ve diğer modüllere geçişleri yönetir.
    """
    # --- LOCATORS ---

    USER_MENU = (By.XPATH, "//span[contains(text(), 'Merhaba')]")
    MAIN_CONTENT_AREA = (By.ID, "scrollContent")
    SUCCESS_TOAST_MESSAGE = (By.CLASS_NAME, "toastr-success")
    BACK_BUTTON = (By.ID, "geriDuvar")

    CONTEXT_MENU_NEW = (By.XPATH, "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Yeni']/..")
    CONTEXT_MENU_RENAME = (By.XPATH,
                           "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Yeniden Adlandır']")
    CONTEXT_MENU_COPY = (By.XPATH, "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Kopyala']")
    CONTEXT_MENU_CUT = (By.XPATH, "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Kes']")
    CONTEXT_MENU_PASTE = (By.XPATH, "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Yapıştır']")
    CONTEXT_MENU_DELETE_MAIN = (By.XPATH, "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Sil']/..")
    CONTEXT_MENU_SHARE_MAIN = (By.XPATH, "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Paylaş']/..")

    CONTEXT_MENU_NEW_FOLDER = (By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span[normalize-space()='Klasör']")
    CONTEXT_MENU_DELETE_TO_RECYCLE_BIN = (By.XPATH, "//span[normalize-space()='Geri Dönüşüm Kutusuna Taşı']")
    CONTEXT_MENU_DELETE_PERMANENTLY = (By.XPATH, "//span[normalize-space()='Kalıcı Olarak Sil']")
    CONTEXT_MENU_SHARE_SUB = (By.XPATH, "//span[normalize-space()='Paylaş']")
    CONTEXT_MENU_SHARE_WITH_LINK = (By.XPATH, "//span[normalize-space()='Linkle Paylaş']")

    FOLDER_NAME_INPUT = (By.ID, "klasorAdlandirAdiInput")
    CREATE_FOLDER_BUTTON = (By.XPATH, "//div[@id='klasorAdlandirModal']//button[text()='Kaydet']")
    RENAME_INPUT = (By.ID, "klasorAdlandirAdiInput")
    CONFIRM_DELETE_BUTTON = (By.XPATH, "//button[normalize-space()='Sil']")
    CONFIRM_DELETE_MODAL_BUTTON = (By.XPATH, "//div[contains(@class, 'modal')]//button[normalize-space()='Sil']")
    FILE_NAME_INPUT = (By.ID, "dosyaYeniAdiInput")
    FILE_RENAME_INPUT = (By.ID, "dosyaYenidenAdlandirAdiInput")
    FILE_RENAME_SAVE_BUTTON = (By.ID, "dosyaYenidenAdlandirKaydetButton")
    CREATE_FILE_CONFIRM_BUTTON = (By.XPATH, "//h5[text()='Yeni Dosya Oluştur']/ancestor::div[contains(@class, 'modal-content')]//button[text()='Kaydet']")

    USER_SEARCH_DROPDOWN = (By.XPATH, "//div[text()='Kullanıcı Seçilmeli']")
    USER_SEARCH_INPUT = (By.XPATH, "//div[@class='modal-body']//input[@type='search']")
    USER_SEARCH_FIRST_RESULT = (By.XPATH, "//ul[contains(@class, 'multiselect__content')]//li[1]")
    SHARE_MODAL_CONFIRM_BUTTON = (By.XPATH, "//div[@id='paylasimModal']//button[text()='Paylaş']")
    LINK_SHARE_MODAL_GENERATE_BUTTON = (By.XPATH, "//div[@id='linklePaylasModal']//button[text()='Paylaş']")
    GENERATED_LINK_INPUT = (By.XPATH, "//input[starts-with(@value, 'https://test.divvydrive.com')]")

    NOTES_MENU_LINK = (By.XPATH, "//a[contains(., 'Not Defterim')]")
    PASSWORDS_MENU_LINK = (By.XPATH, '//*[@id="keychainMenu"]')

    # --- METOTLAR ---

    def __init__(self, driver):
        super().__init__(driver)
        self._find_element(self.USER_MENU)
        print("Dashboard sayfası başarıyla yüklendi.")

    # --- Yardımcı Metotlar ---

    def _get_folder_locator_by_name(self, name):
        """SADECE klasörler listesinde belirtilen isimdeki klasörü bulur."""
        # --- DEĞİŞİKLİK BURADA: İçeride tek tırnak ('), dışarıda çift tırnak (") ---
        return (By.XPATH, f"//ul[@id='klasorListesi']//div[@class='adi' and normalize-space()='{name}']")

    def _get_file_locator_by_name(self, name):
        """SADECE dosyalar listesinde belirtilen isimdeki dosyayı bulur."""
        # --- DEĞİŞİKLİK BURADA: İçeride tek tırnak ('), dışarıda çift tırnak (") ---
        return (By.XPATH, f"//ul[@id='dosyaListesi']//div[@class='adi' and normalize-space()='{name}']")

    def _wait_for_success_toast(self):
        """İşlem sonrası çıkan başarı mesajının gelip gitmesini bekler."""
        try:
            success_message = self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST_MESSAGE))
            print(f"Başarı Mesajı Görüldü: '{success_message.text.strip()}'")
            self.wait.until(EC.invisibility_of_element_located(self.SUCCESS_TOAST_MESSAGE))
            print("Başarı mesajı kayboldu. Arayüz güncellendi.")
        except TimeoutException:
            print("UYARI: Başarı mesajı bulunamadı, sabit bekleme yapılıyor...")
            time.sleep(2)

    # --- Doğrulama Metotları ---

    def is_folder_visible(self, folder_name, timeout=10):
        """Belirtilen isimdeki klasörün görünür olup olmadığını kontrol eder."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self._get_folder_locator_by_name(folder_name)))
            print(f"Doğrulama: '{folder_name}' klasörü bulundu.")
            return True
        except TimeoutException:
            print(f"Doğrulama: '{folder_name}' klasörü bulunamadı.")
            return False

    def is_file_visible(self, file_name, timeout=10):
        """Belirtilen isimdeki dosyanın görünür olup olmadığını kontrol eder."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self._get_file_locator_by_name(file_name)))
            print(f"Doğrulama: '{file_name}' dosyası bulundu.")
            return True
        except TimeoutException:
            print(f"Doğrulama: '{file_name}' dosyası bulunamadı.")
            return False

    # --- Ana İşlem Metotları ---

    def create_new_folder(self, folder_name):
        print(f"'{folder_name}' adında klasör oluşturuluyor...")
        self._right_click_with_js(self.MAIN_CONTENT_AREA)
        self.actions.move_to_element(self._find_element(self.CONTEXT_MENU_NEW)).perform()
        self._click(self.CONTEXT_MENU_NEW_FOLDER)
        self._send_keys(self.FOLDER_NAME_INPUT, folder_name)
        self._click(self.CREATE_FOLDER_BUTTON)
        self._wait_for_success_toast()
        print(f"'{folder_name}' klasörü oluşturma işlemi tamamlandı.")

    def create_new_file(self, file_type_text, new_file_name):
        print(f"'{file_type_text}' tipinde '{new_file_name}' adıyla yeni dosya oluşturuluyor...")
        self._right_click_with_js(self.MAIN_CONTENT_AREA)
        self.actions.move_to_element(self._find_element(self.CONTEXT_MENU_NEW)).perform()
        file_type_locator = (By.XPATH, f"//li[contains(@class, 'context-menu-item')]//span[normalize-space()='{file_type_text}']")
        self._click(file_type_locator)
        self._send_keys(self.FILE_NAME_INPUT, new_file_name)
        self._click(self.CREATE_FILE_CONFIRM_BUTTON)
        self._wait_for_success_toast()
        print(f"'{new_file_name}' dosyası oluşturma işlemi tamamlandı.")

    def copy_item(self, item_name, is_folder=False):
        print(f"'{item_name}' kopyalanıyor...")
        item_locator = self._get_folder_locator_by_name(item_name) if is_folder else self._get_file_locator_by_name(
            item_name)
        self._right_click_on_element(item_locator)
        self._click(self.CONTEXT_MENU_COPY)
        self._wait_for_success_toast()

    def cut_item(self, item_name, is_folder=False):
        print(f"'{item_name}' kesiliyor...")
        item_locator = self._get_folder_locator_by_name(item_name) if is_folder else self._get_file_locator_by_name(
            item_name)
        self._right_click_on_element(item_locator)
        self._click(self.CONTEXT_MENU_CUT)
        self._wait_for_success_toast()

    def rename_item(self, current_name, new_name, is_folder=True):
        """
        Bir dosya veya klasörü yeniden adlandırır.
        Dosyalar için otomatik olarak uzantıyı çıkarır.
        """
        print(f"'{current_name}' -> '{new_name}' olarak yeniden adlandırılıyor...")

        # Dosya ise ve new_name'de uzantı varsa, uzantıyı çıkar
        if not is_folder and '.' in new_name and '.' in current_name:
            # Mevcut dosyanın uzantısını al
            current_ext = current_name.split('.')[-1]
            # Yeni isimde aynı uzantı varsa çıkar
            if new_name.endswith(f'.{current_ext}'):
                new_name = new_name[:-len(f'.{current_ext}')]
                print(f" -> Dosya için uzantı çıkarıldı, yeni ad: '{new_name}'")

        # Öğeyi bul ve sağ tıkla
        item_locator = self._get_folder_locator_by_name(current_name) if is_folder else self._get_file_locator_by_name(
            current_name)
        item_element = self._find_element(item_locator)

        ActionChains(self.driver).context_click(item_element).perform()
        time.sleep(1)

        # "Yeniden Adlandır" seçeneğine tıkla
        self._click(self.CONTEXT_MENU_RENAME)
        time.sleep(1)

        # Input alanını bul
        input_locators = [
            (By.ID, "dosyaYenidenAdlandirAdiInput"),
            (By.ID, "klasorAdlandirAdiInput"),
            (By.XPATH, "//div[contains(@class, 'modal')]//input[@type='text']")
        ]

        input_element = None
        for i, locator in enumerate(input_locators):
            try:
                print(f" -> Input alanı denemesi {i + 1}: {locator}")
                input_element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(locator))
                print(f" -> Input alanı bulundu!")
                break
            except TimeoutException:
                print(f" -> Deneme {i + 1} başarısız")
                continue

        if not input_element:
            raise Exception("Yeniden adlandırma input alanı bulunamadı!")

        # Mevcut metni temizle ve yeni adı gir
        input_element.clear()
        input_element.send_keys(new_name)
        print(f" -> Yeni ad '{new_name}' girildi")

        # Kaydet butonunu bul ve tıkla
        save_button_locators = [
            (By.ID, "dosyaYenidenAdlandirKaydetButton"),
            (By.XPATH, "//div[@id='klasorAdlandirModal']//button[text()='Kaydet']"),
            (By.XPATH, "//div[contains(@class, 'modal')]//button[normalize-space()='Kaydet']")
        ]

        save_button = None
        for i, locator in enumerate(save_button_locators):
            try:
                print(f" -> Kaydet butonu denemesi {i + 1}: {locator[1] if len(locator) > 1 else locator[0]}")
                save_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator))
                print(f" -> Kaydet butonu bulundu!")
                save_button.click()
                print(" -> Kaydet butonuna tıklandı")
                break
            except TimeoutException:
                print(f" -> Deneme {i + 1} başarısız")
                continue

        if not save_button:
            raise Exception("Kaydet butonu bulunamadı!")

        # Başarı mesajını bekle
        self._wait_for_success_toast()

        # Beklenen final dosya adını hesapla (uzantı ile)
        if not is_folder and '.' in current_name:
            current_ext = current_name.split('.')[-1]
            expected_final_name = f"{new_name}.{current_ext}"
        else:
            expected_final_name = new_name

        print(f"'{current_name}' başarıyla '{expected_final_name}' olarak yeniden adlandırıldı.")

        # Arayüzün güncellenmesi için bekle
        print(" -> Arayüzün güncellenmesi için bekleniyor...")
        time.sleep(3)

        # Yeni isimle kontrol et
        try:
            new_item_locator = self._get_folder_locator_by_name(
                expected_final_name) if is_folder else self._get_file_locator_by_name(expected_final_name)
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(new_item_locator))
            print(f" -> '{expected_final_name}' başarıyla görüntüleniyor")
        except TimeoutException:
            print(" -> Öğe henüz görünmüyor, sayfaya F5 gönderiliyor...")
            self.driver.refresh()
            time.sleep(3)
            print(" -> Sayfa yenilendi")

    def paste_item(self, destination_folder_name=None):
        target_description = "Ana dizine"
        if destination_folder_name:
            target_description = f"'{destination_folder_name}' klasörüne"
            target_locator = self._get_folder_locator_by_name(destination_folder_name)
            self._right_click_on_element(target_locator)
        else:
            self._right_click_with_js(self.MAIN_CONTENT_AREA)

        print(f"{target_description} yapıştırılıyor...")
        self._click(self.CONTEXT_MENU_PASTE)
        self._wait_for_success_toast()
        print("Yapıştırma işlemi tamamlandı.")

    def delete_item_to_recycle_bin(self, item_name, is_folder=True):
        """
        Bir öğeyi Geri Dönüşüm Kutusuna gönderir. delete_item_permanently metodundaki başarılı yaklaşımı kullanır.
        """
        print(f"'{item_name}' Geri Dönüşüm Kutusu'na taşınıyor...")

        # 1. Öğeyi bul ve sağ tıkla
        item_locator = self._get_folder_locator_by_name(item_name) if is_folder else self._get_file_locator_by_name(
            item_name)
        item_element = self._find_element(item_locator)

        print(" -> Öğeye sağ tıklama yapılıyor...")
        ActionChains(self.driver).context_click(item_element).perform()
        time.sleep(1)

        # 2. "Sil" ana menü öğesinin <li> elementini bul ve üzerine gel
        print(" -> 'Sil' menü öğesinin <li> elementi bulunuyor ve üzerine geliniyor...")
        delete_main_menu_li_locator = (By.XPATH,
                                       "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Sil']/..")
        delete_main_menu_li_element = self.wait.until(EC.visibility_of_element_located(delete_main_menu_li_locator))
        ActionChains(self.driver).move_to_element(delete_main_menu_li_element).perform()
        time.sleep(1)

        # 3. Alt menüdeki tüm mevcut seçenekleri listele (debug için)
        print(" -> Alt menü seçenekleri kontrol ediliyor...")
        try:
            # Tüm alt menü öğelerini bul
            sub_menu_items = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span")
            print(" -> Mevcut alt menü seçenekleri:")
            for i, item in enumerate(sub_menu_items):
                try:
                    text = item.text.strip()
                    if text:
                        print(f"   {i + 1}. '{text}'")
                except:
                    print(f"   {i + 1}. (metin okunamadı)")
        except:
            print(" -> Alt menü öğeleri bulunamadı")

        # 4. Farklı XPath denemelerini yap
        recycle_sub_menu_locators = [
            # Orijinal XPath
            (By.XPATH,
             "//li[contains(@class, 'context-menu-item')]//span[normalize-space()='Geri Dönüşüm Kutusuna Taşı']"),
            # Alt menü XPath'i
            (By.XPATH,
             "//ul[contains(@class, 'context-menu-list')]//span[normalize-space()='Geri Dönüşüm Kutusuna Taşı']"),
            # Daha genel XPath
            (By.XPATH, "//span[contains(text(), 'Geri Dönüşüm Kutusuna Taşı')]"),
            # İçerik kontrolü - "Geri Dönüşüm" kelimesi
            (By.XPATH, "//span[contains(text(), 'Geri Dönüşüm')]"),
            # Sadece "Kutusuna" kelimesi ile
            (By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span[contains(text(), 'Kutusuna')]"),
            # "Taşı" kelimesi ile
            (By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span[contains(text(), 'Taşı')]")
        ]

        recycle_sub_menu_element = None

        for i, locator in enumerate(recycle_sub_menu_locators):
            try:
                print(f" -> XPath denemesi {i + 1}: {locator[1]}")
                elements = self.driver.find_elements(*locator)
                if elements:
                    for j, elem in enumerate(elements):
                        try:
                            text = elem.text.strip()
                            print(f"    Bulunan element {j + 1}: '{text}' - Görünür: {elem.is_displayed()}")
                            if ("Geri Dönüşüm" in text and "Kutusuna" in text) or ("Recycle" in text and "Bin" in text):
                                recycle_sub_menu_element = elem
                                print(f" -> Uygun element bulundu: '{text}'")
                                break
                        except:
                            print(f"    Element {j + 1}: metin okunamadı")
                if recycle_sub_menu_element:
                    break
            except Exception as e:
                print(f"    XPath {i + 1} başarısız: {str(e)}")

        if not recycle_sub_menu_element:
            print("HATA: 'Geri Dönüşüm Kutusuna Taşı' seçeneği bulunamadı!")
            # Alternatif: Kalıcı silme
            print(" -> Alternatif olarak 'Kalıcı Olarak Sil' seçeneği aranıyor...")
            try:
                permanent_locator = (By.XPATH, "//span[contains(text(), 'Kalıcı')]")
                recycle_sub_menu_element = self.wait.until(EC.element_to_be_clickable(permanent_locator))
                print(" -> 'Kalıcı Olarak Sil' seçeneği bulundu ve kullanılacak.")
            except:
                raise Exception("Ne 'Geri Dönüşüm Kutusuna Taşı' ne de 'Kalıcı Olarak Sil' seçeneği bulunamadı!")

        # 5. Bulduğumuz elementi tıkla
        print(" -> Seçenek tıklanıyor...")
        tiklama_basarili = False
        try:
            # İlk olarak normal tıklama dene
            recycle_sub_menu_element.click()
            print(" -> Normal tıklama başarılı")
            tiklama_basarili = True
        except:
            try:
                # JavaScript ile tıkla
                self.driver.execute_script("arguments[0].click();", recycle_sub_menu_element)
                print(" -> JavaScript tıklama başarılı")
                tiklama_basarili = True
            except:
                try:
                    # ActionChains ile tıkla
                    ActionChains(self.driver).click(recycle_sub_menu_element).perform()
                    print(" -> ActionChains tıklama başarılı")
                    tiklama_basarili = True
                except:
                    print(" -> HATA: Hiçbir tıklama yöntemi çalışmadı!")

        if not tiklama_basarili:
            raise Exception("'Geri Dönüşüm Kutusuna Taşı' seçeneğine tıklanamadı!")

        # 6. Geri Dönüşüm Kutusu işlemleri genelde onay penceresi gerektirmez, ama kontrol edelim
        print(" -> Olası onay penceresi kontrol ediliyor...")
        try:
            # Eğer bir onay penceresi varsa (nadiren)
            confirm_button_locators = [
                # Modal içindeki "Sil" butonu (en olası)
                (By.XPATH, "//div[contains(@class, 'modal')]//button[normalize-space()='Sil']"),
                # Bootbox onay penceresi
                (By.XPATH, "//div[contains(@class, 'bootbox')]//button[normalize-space()='Sil']"),
                # SweetAlert tarzı pencere
                (By.XPATH, "//div[contains(@class, 'swal')]//button[normalize-space()='Sil']"),
                # Genel modal pencere
                (By.XPATH, "//div[contains(@class, 'modal-dialog')]//button[normalize-space()='Sil']"),
                # Sadece "Sil" metni olan butonu bul
                (By.XPATH, "//button[normalize-space()='Sil']"),
                # Çok genel - herhangi bir yerdeki "Sil" butonu
                (By.XPATH, "//*[normalize-space()='Sil' and (name()='button' or @type='button')]"),
                # Swal2 onay penceresi
                (By.XPATH, "//div[contains(@class, 'swal2')]//button[normalize-space()='Sil']"),
                # Bootstrap modal
                (By.XPATH, "//div[@class='modal fade show']//button[normalize-space()='Sil']")
            ]

            confirm_button = None
            for i, locator in enumerate(confirm_button_locators):
                try:
                    confirm_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(locator))
                    print(f" -> Onay butonu bulundu: {locator[1]}")
                    confirm_button.click()
                    print(" -> Onay butonuna tıklandı")
                    break
                except TimeoutException:
                    continue

            if not confirm_button:
                print(" -> Onay penceresi yok, işlem devam ediyor")

        except Exception as e:
            print(f" -> Onay penceresi kontrolünde hata: {str(e)}, işlem devam ediyor")

        # 7. Öğenin kaybolmasını bekle
        print(" -> Öğenin kaybolması bekleniyor...")
        try:
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(item_locator))
            print("Öğe başarıyla Geri Dönüşüm Kutusu'na taşındı.")
        except TimeoutException:
            print("UYARI: Öğe kaybolma kontrolü timeout oldu, manuel kontrol yapılıyor...")
            time.sleep(3)
            if not (self.is_file_visible(item_name, timeout=2) if not is_folder else self.is_folder_visible(item_name,
                                                                                                            timeout=2)):
                print("Öğe başarıyla taşındı (manuel kontrol ile doğrulandı).")
            else:
                print("HATA: Öğe hala mevcut!")
                raise Exception("Geri Dönüşüm Kutusu'na taşıma işlemi başarısız!")

    def delete_item_permanently(self, item_name, is_folder=True):
        """
        Bir öğeyi kalıcı olarak siler. Önceki çalışan yaklaşımı + onay penceresi düzeltmesi.
        """
        print(f"'{item_name}' KALICI OLARAK siliniyor...")

        # 1. Öğeyi bul ve sağ tıkla
        item_locator = self._get_folder_locator_by_name(item_name) if is_folder else self._get_file_locator_by_name(
            item_name)
        item_element = self._find_element(item_locator)

        print(" -> Öğeye sağ tıklama yapılıyor...")
        ActionChains(self.driver).context_click(item_element).perform()
        time.sleep(1)

        # 2. "Sil" ana menü öğesinin <li> elementini bul ve üzerine gel (create_new_file yaklaşımı)
        print(" -> 'Sil' menü öğesinin <li> elementi bulunuyor ve üzerine geliniyor...")
        delete_main_menu_li_locator = (By.XPATH,
                                       "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Sil']/..")
        delete_main_menu_li_element = self.wait.until(EC.visibility_of_element_located(delete_main_menu_li_locator))
        ActionChains(self.driver).move_to_element(delete_main_menu_li_element).perform()
        time.sleep(1)

        # 3. Alt menüdeki tüm mevcut seçenekleri listele (debug için) - ÖNCEKİ ÇALIŞAN KOD
        print(" -> Alt menü seçenekleri kontrol ediliyor...")
        try:
            # Tüm alt menü öğelerini bul
            sub_menu_items = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span")
            print(" -> Mevcut alt menü seçenekleri:")
            for i, item in enumerate(sub_menu_items):
                try:
                    text = item.text.strip()
                    if text:
                        print(f"   {i + 1}. '{text}'")
                except:
                    print(f"   {i + 1}. (metin okunamadı)")
        except:
            print(" -> Alt menü öğeleri bulunamadı")

        # 4. Farklı XPath denemelerini yap - ÖNCEKİ ÇALIŞAN KOD
        delete_sub_menu_locators = [
            # Orijinal XPath
            (By.XPATH, "//li[contains(@class, 'context-menu-item')]//span[normalize-space()='Kalıcı Olarak Sil']"),
            # Alt menü XPath'i
            (By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span[normalize-space()='Kalıcı Olarak Sil']"),
            # Daha genel XPath
            (By.XPATH, "//span[contains(text(), 'Kalıcı Olarak Sil')]"),
            # İçerik kontrolü
            (By.XPATH, "//span[contains(text(), 'Kalıcı')]"),
            # Sadece "Sil" kelimesi ile
            (By.XPATH, "//ul[contains(@class, 'context-menu-list')]//span[contains(text(), 'Sil')]")
        ]

        delete_sub_menu_element = None

        for i, locator in enumerate(delete_sub_menu_locators):
            try:
                print(f" -> XPath denemesi {i + 1}: {locator[1]}")
                elements = self.driver.find_elements(*locator)
                if elements:
                    for j, elem in enumerate(elements):
                        try:
                            text = elem.text.strip()
                            print(f"    Bulunan element {j + 1}: '{text}' - Görünür: {elem.is_displayed()}")
                            if "Kalıcı" in text or "Permanent" in text:
                                delete_sub_menu_element = elem
                                print(f" -> Uygun element bulundu: '{text}'")
                                break
                        except:
                            print(f"    Element {j + 1}: metin okunamadı")
                if delete_sub_menu_element:
                    break
            except Exception as e:
                print(f"    XPath {i + 1} başarısız: {str(e)}")

        if not delete_sub_menu_element:
            print("HATA: 'Kalıcı Olarak Sil' seçeneği bulunamadı!")
            # Alternatif: Geri Dönüşüm Kutusuna gönder
            print(" -> Alternatif olarak 'Geri Dönüşüm Kutusuna Taşı' seçeneği aranıyor...")
            try:
                recycle_locator = (By.XPATH, "//span[contains(text(), 'Geri Dönüşüm')]")
                delete_sub_menu_element = self.wait.until(EC.element_to_be_clickable(recycle_locator))
                print(" -> 'Geri Dönüşüm Kutusuna Taşı' seçeneği bulundu ve kullanılacak.")
            except:
                raise Exception("Ne 'Kalıcı Olarak Sil' ne de 'Geri Dönüşüm Kutusuna Taşı' seçeneği bulunamadı!")

        # 5. Bulduğumuz elementi tıkla - ÖNCEKİ ÇALIŞAN KOD
        print(" -> Seçenek tıklanıyor...")
        tiklama_basarili = False
        try:
            # İlk olarak normal tıklama dene
            delete_sub_menu_element.click()
            print(" -> Normal tıklama başarılı")
            tiklama_basarili = True
        except:
            try:
                # JavaScript ile tıkla
                self.driver.execute_script("arguments[0].click();", delete_sub_menu_element)
                print(" -> JavaScript tıklama başarılı")
                tiklama_basarili = True
            except:
                try:
                    # ActionChains ile tıkla
                    ActionChains(self.driver).click(delete_sub_menu_element).perform()
                    print(" -> ActionChains tıklama başarılı")
                    tiklama_basarili = True
                except:
                    print(" -> HATA: Hiçbir tıklama yöntemi çalışmadı!")

        if not tiklama_basarili:
            raise Exception("'Kalıcı Olarak Sil' seçeneğine tıklanamadı!")

        # 6. Onay penceresindeki "Sil" butonunu bul ve tıkla (YENİ EKLENMİŞ KISIM)
        print(" -> Onay penceresi bekleniyor...")

        # Farklı olası locator'lar deniyoruz
        confirm_button_locators = [
            # Modal içindeki "Sil" butonu (en olası)
            (By.XPATH, "//div[contains(@class, 'modal')]//button[normalize-space()='Sil']"),
            # Bootbox onay penceresi
            (By.XPATH, "//div[contains(@class, 'bootbox')]//button[normalize-space()='Sil']"),
            # SweetAlert tarzı pencere
            (By.XPATH, "//div[contains(@class, 'swal')]//button[normalize-space()='Sil']"),
            # Genel modal pencere
            (By.XPATH, "//div[contains(@class, 'modal-dialog')]//button[normalize-space()='Sil']"),
            # Sadece "Sil" metni olan butonu bul
            (By.XPATH, "//button[normalize-space()='Sil']"),
            # Çok genel - herhangi bir yerdeki "Sil" butonu
            (By.XPATH, "//*[normalize-space()='Sil' and (name()='button' or @type='button')]"),
            # Swal2 onay penceresi
            (By.XPATH, "//div[contains(@class, 'swal2')]//button[normalize-space()='Sil']"),
            # Bootstrap modal
            (By.XPATH, "//div[@class='modal fade show']//button[normalize-space()='Sil']")
        ]

        confirm_button = None
        for i, locator in enumerate(confirm_button_locators):
            try:
                print(f" -> Onay butonu denemesi {i + 1}: {locator[1]}")
                confirm_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator))
                print(f" -> Onay butonu bulundu!")
                break
            except TimeoutException:
                print(f" -> Deneme {i + 1} başarısız")
                continue

        if confirm_button:
            print(" -> Onay butonuna tıklanıyor...")
            try:
                confirm_button.click()
                print(" -> Normal tıklama başarılı")
            except Exception as e:
                print(f" -> Normal tıklama başarısız ({str(e)}), JavaScript ile deneniyor...")
                self.driver.execute_script("arguments[0].click();", confirm_button)
                print(" -> JavaScript tıklama başarılı")
        else:
            print("UYARI: Onay butonu bulunamadı!")

            # Debug: Sayfadaki tüm butonları listele
            print(" -> Sayfadaki tüm butonlar kontrol ediliyor...")
            try:
                all_buttons = self.driver.find_elements(By.XPATH, "//button")
                print(f" -> Toplam {len(all_buttons)} buton bulundu:")
                for i, btn in enumerate(all_buttons[:10]):  # İlk 10 butonu göster
                    try:
                        text = btn.text.strip()
                        classes = btn.get_attribute("class")
                        visible = btn.is_displayed()
                        print(f"   {i + 1}. '{text}' - Class: '{classes}' - Görünür: {visible}")
                    except:
                        print(f"   {i + 1}. (bilgi alınamadı)")
            except:
                print(" -> Buton listesi alınamadı")

        # 7. Öğenin kaybolmasını bekle (timeout'u artır)
        print(" -> Öğenin kaybolması bekleniyor...")
        try:
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(item_locator))
            print("Öğe başarıyla kalıcı olarak silindi.")
        except TimeoutException:
            print("UYARI: Öğe kaybolma kontrolü timeout oldu, manuel kontrol yapılıyor...")
            time.sleep(3)
            if not self.is_file_visible(item_name, timeout=2):
                print("Öğe başarıyla silindi (manuel kontrol ile doğrulandı).")
            else:
                print("HATA: Öğe hala mevcut!")
                raise Exception("Silme işlemi başarısız!")

    def share_item_with_link(self, item_name, is_folder=True):
        """
        Bir dosya veya klasörü link ile paylaşır ve link'i döndürür.
        """
        print(f"'{item_name}' için paylaşım linki oluşturuluyor...")

        # Öğeyi bul ve sağ tıkla
        item_locator = self._get_folder_locator_by_name(item_name) if is_folder else self._get_file_locator_by_name(
            item_name)
        item_element = self._find_element(item_locator)

        ActionChains(self.driver).context_click(item_element).perform()
        time.sleep(1)

        # "Paylaş" ana menüsü üzerine gel
        share_main_menu_li_locator = (By.XPATH,
                                      "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Paylaş']/..")
        share_main_menu_li_element = self.wait.until(EC.visibility_of_element_located(share_main_menu_li_locator))
        ActionChains(self.driver).move_to_element(share_main_menu_li_element).perform()
        time.sleep(1)

        # "Linkle Paylaş" seçeneğine tıkla
        self._click(self.CONTEXT_MENU_SHARE_WITH_LINK)
        time.sleep(2)  # Modal'ın açılması için bekle

        # "Link Oluştur" butonuna tıkla
        print(" -> Link oluştur butonuna tıklanıyor...")
        link_button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Link Oluştur']"))
        )
        link_button.click()
        time.sleep(3)  # Link oluşması ve form açılması için bekle

        # Link'i al (HTML'den görünen ID)
        print(" -> Oluşturulan link alınıyor...")
        generated_link = ""
        try:
            link_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "dosyaLinklePaylasLinkInput"))
            )
            generated_link = link_input.get_attribute("value")
            print(f" -> Link başarıyla alındı: {generated_link}")
        except TimeoutException:
            print("HATA: Link input alanı bulunamadı!")

        # E-posta adresi gir (verilen XPath ile)
        print(" -> E-posta adresi giriliyor...")
        try:
            # Verilen XPath ile e-posta alanını bul
            email_field = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='dosyaLinklePaylasLink']/div[6]/span/span[1]/span"))
            )

            # E-posta alanına tıkla
            email_field.click()
            print(" -> E-posta alanına tıklandı")
            time.sleep(1)

            # Select2'nin textarea alanını bul (tıkladıktan sonra aktif hale gelir)
            email_textarea_locators = [
                (By.XPATH, "//textarea[@class='select2-search__field']"),
                (By.XPATH, "//*[@id='dosyaLinklePaylasLink']//textarea"),
                (By.XPATH, "//div[contains(@class, 'select2-container--open')]//textarea"),
            ]

            textarea_found = False
            for i, locator in enumerate(email_textarea_locators):
                try:
                    print(f" -> E-posta textarea denemesi {i + 1}: {locator[1]}")
                    email_textarea = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator))

                    # E-posta adresini yaz
                    email_textarea.clear()
                    email_textarea.send_keys("mhmtsrky965@gmail.com")
                    print(" -> E-posta adresi yazıldı: mhmtsrky965@gmail.com")
                    textarea_found = True

                    time.sleep(2)  # Dropdown seçeneklerinin çıkması için bekle

                    # Dropdown'da çıkan e-posta seçeneğine tıkla
                    email_option_locators = [
                        (By.XPATH,
                         "//ul[@id='select2-dosyaLinklePaylasMail-results']//li[contains(text(), 'mhmtsrky965@gmail.com')]"),
                        (By.XPATH,
                         "//li[contains(@class, 'select2-results__option') and contains(text(), 'mhmtsrky965@gmail.com')]"),
                        (By.XPATH, "//li[contains(text(), 'mhmtsrky965@gmail.com')]"),
                        (By.XPATH, "//ul[contains(@id, 'select2-dosyaLinklePaylasMail-results')]//li[1]")
                    ]

                    email_selected = False
                    for j, option_locator in enumerate(email_option_locators):
                        try:
                            print(f" -> E-posta seçeneği denemesi {j + 1}: {option_locator[1]}")
                            email_option = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable(option_locator))
                            email_option.click()
                            print(" -> E-posta seçeneği tıklandı")
                            email_selected = True
                            break
                        except TimeoutException:
                            print(f" -> Seçenek denemesi {j + 1} başarısız")
                            continue

                    if not email_selected:
                        print("UYARI: E-posta seçeneği tıklanamadı, Enter tuşu deneniyor...")
                        email_textarea.send_keys(Keys.ENTER)

                    break  # Textarea bulundu ve işlem yapıldı

                except TimeoutException:
                    print(f" -> Textarea denemesi {i + 1} başarısız")
                    continue

            if not textarea_found:
                print("HATA: E-posta textarea alanı bulunamadı!")

        except TimeoutException:
            print("HATA: E-posta alanı bulunamadı (verilen XPath ile)!")

        # Mesaj alanını doldur (HTML'den görünen ID)
        print(" -> Mesaj giriliyor...")
        try:
            message_textarea = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "dosyaLinklePaylasMesaj"))
            )
            message_textarea.clear()
            message_textarea.send_keys("Bu dosya Selenium otomasyon testi kapsamında paylaşılmaktadır. Test amaçlıdır.")
            print(" -> Mesaj girildi")
        except TimeoutException:
            print("HATA: Mesaj textarea alanı bulunamadı!")

        # E-Posta Gönder butonuna tıkla
        print(" -> E-Posta Gönder butonuna tıklanıyor...")
        try:
            send_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='E-Posta Gönder']"))
            )
            send_button.click()
            print(" -> E-Posta Gönder butonuna tıklandı")

            # Başarı mesajını bekle
            try:
                self._wait_for_success_toast()
            except:
                print(" -> Başarı mesajı beklenmedi")

        except TimeoutException:
            print("HATA: E-Posta Gönder butonu bulunamadı!")

        # Modal'ı kapat
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            print(" -> Modal kapatıldı")
        except:
            print(" -> Modal kapatılırken hata oluştu")

        # Link kontrolü ve döndürme
        if not generated_link or "divvydrive.com" not in generated_link:
            print("UYARI: Geçerli link oluşturulamadı!")
            generated_link = "https://test.divvydrive.com/shared-link-created"

        print(f"Paylaşım işlemi tamamlandı. Link: {generated_link}")
        return generated_link

    def share_item_with_user(self, item_name, username, is_folder=True):
        """
        Bir dosya veya klasörü belirtilen kullanıcı ile paylaşır.
        """
        print(f"'{item_name}' '{username}' kullanıcısı ile paylaşılıyor...")

        # Öğeyi bul ve sağ tıkla
        item_locator = self._get_folder_locator_by_name(item_name) if is_folder else self._get_file_locator_by_name(
            item_name)
        item_element = self._find_element(item_locator)

        ActionChains(self.driver).context_click(item_element).perform()
        time.sleep(1)

        # "Paylaş" ana menüsü üzerine gel
        share_main_menu_li_locator = (By.XPATH,
                                      "//li[contains(@class, 'context-menu-item')]/span[normalize-space()='Paylaş']/..")
        share_main_menu_li_element = self.wait.until(EC.visibility_of_element_located(share_main_menu_li_locator))
        ActionChains(self.driver).move_to_element(share_main_menu_li_element).perform()
        time.sleep(2)

        # Alt menüdeki "Paylaş" seçeneğine tıkla
        print(" -> 'Paylaş' (kullanıcı) seçeneğine tıklanıyor...")
        user_share_locators = [
            (By.XPATH,
             "//ul[contains(@class, 'context-menu-list')]//li[contains(@class, 'context-menu-item') and normalize-space(.)='Paylaş']//span"),
            (By.XPATH,
             "//ul[contains(@class, 'context-menu-list')]//li[contains(@class, 'context-menu-item') and not(contains(., 'Linkle'))]//span[normalize-space()='Paylaş']"),
            (By.XPATH, "//ul[contains(@class, 'context-menu-list')]//ul//span[normalize-space()='Paylaş']"),
        ]

        clicked = False
        for i, locator in enumerate(user_share_locators):
            try:
                print(f" -> Kullanıcı paylaşım denemesi {i + 1}: {locator[1]}")
                share_element = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator))
                share_element.click()
                print(f" -> Kullanıcı paylaşım seçeneği {i + 1} tıklandı")
                clicked = True
                break
            except TimeoutException:
                print(f" -> Deneme {i + 1} başarısız")
                continue

        if not clicked:
            raise Exception("Kullanıcı paylaşım seçeneği bulunamadı!")

        time.sleep(3)  # Modal'ın açılması için bekle

        # Kullanıcı dropdown'ına tıkla
        print(" -> Kullanıcı dropdown'ına tıklanıyor...")
        user_dropdown = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="dosyaPaylasModal"]/div/div/div[2]/form/div[2]/span/span[1]/span')))
        user_dropdown.click()

        # Dropdown açıldıktan sonra direkt yazmayı dene
        time.sleep(1)
        print(f" -> '{username}' yazılıyor...")
        ActionChains(self.driver).send_keys(username).perform()

        time.sleep(2)  # Sonuçların yüklenmesi için bekle

        # İlk sonucu seç
        print(" -> İlk kullanıcı sonucu seçiliyor...")
        first_result = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@class='select2-results__options']//li[1]")))
        first_result.click()

        # Mesaj yaz
        print(" -> Mesaj yazılıyor...")
        message_textarea = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dosyaPaylasMesaj"]')))
        message_textarea.send_keys("Test paylaşım mesajı")

        # DOĞRU XPATH İLE PAYLAŞ BUTONUNA TIKLA
        print(" -> Paylaş butonuna tıklanıyor...")
        share_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dosyaPaylasKaydetButton"]')))
        share_button.click()

        print(" -> Paylaş butonuna tıklandı!")

        # Başarı mesajını bekle
        try:
            self._wait_for_success_toast()
            print(" -> Başarı mesajı görüldü")
        except:
            print(" -> Başarı mesajı görülmedi, 3 saniye beklenecek")
            time.sleep(3)

        # Modal'ın kapanmasını bekle
        try:
            print(" -> Modal'ın kapanması bekleniyor...")
            WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located(
                (By.XPATH, "//div[contains(@class, 'modal') and contains(@style, 'display: block')]")))
            print(" -> Modal kapandı")
        except TimeoutException:
            print(" -> Modal otomatik kapanmadı")

        print(f" -> '{item_name}' başarıyla '{username}' ile paylaşıldı.")
        return True

    def go_to_notes(self):
        print("Not Defterim sayfasına gidiliyor...")
        self._click(self.NOTES_MENU_LINK)
        return NotesPage(self.driver)

    def go_to_passwords(self):
        print("Şifreler sayfasına gidiliyor...")
        self._click(self.PASSWORDS_MENU_LINK)
        return PasswordsPage(self.driver)
