import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, scrolledtext, Toplevel, Button
import hashlib
import gnupg
import os
import shutil

class FileHasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ODEV1")
        self.root.geometry("850x700")

        self.filepath = None
        self.original_hashes = {}
        self.chunks_source_dir = None

        try:
            self.gpg = gnupg.GPG()
            self.gpg.list_keys()
        except (FileNotFoundError, OSError):
             messagebox.showerror("GnuPG Bulunamadı", "GnuPG (GPG) sisteminizde kurulu değil veya PATH içinde bulunmuyor.")
             self.root.destroy()
             return

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        self.file_label = tk.Label(top_frame, text="Lütfen bir dosya seçip 1. adımı çalıştırın.", relief=tk.SUNKEN, anchor="w", padx=5)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        control_frame = tk.Frame(self.root, padx=10, pady=5)
        control_frame.pack(fill=tk.X)
        
        hash_button = tk.Button(control_frame, text="1. Hashle ve Parçalara Ayır", command=self.hash_and_split_file, width=25, height=2)
        hash_button.pack(side=tk.LEFT, padx=5)
        encrypt_button = tk.Button(control_frame, text="2. Şifrele (Bütün & Parçalar)", command=self.encrypt_all, width=25, height=2)
        encrypt_button.pack(side=tk.LEFT, padx=5)
        decrypt_button = tk.Button(control_frame, text="3. Şifre Çöz (Bütün & Parçalar)", command=self.show_decrypt_options, width=25, height=2)
        decrypt_button.pack(side=tk.LEFT, padx=5)
        
        results_frame = tk.Frame(self.root, padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=25, font=("Courier New", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.tag_config('bold', font=("Courier New", 9, 'bold'))
        self.results_text.tag_config('success', foreground="#008B00")
        self.results_text.tag_config('error', foreground="red")
        self.results_text.tag_config('info', foreground="blue")

   
    def _update_status(self, message, tag=None):
        self.results_text.insert(tk.END, message, tag)
        self.results_text.see(tk.END)
        self.root.update_idletasks()

    def _split_file_generator(self, file_path, chunk_size=1024*1024):
        with open(file_path, "rb") as file:
            index = 0
            while (chunk := file.read(chunk_size)):
                yield index, chunk
                index += 1

    def hash_and_split_file(self):
        filepath = filedialog.askopenfilename()
        if not filepath: return

        self.filepath = filepath
        self.file_label.config(text=f"İşleniyor: {os.path.basename(self.filepath)}")
        self.results_text.delete('1.0', tk.END)
        
        base_dir = os.path.dirname(self.filepath)
        file_name_base, _ = os.path.splitext(os.path.basename(self.filepath))
        self.chunks_source_dir = os.path.join(base_dir, f"{file_name_base}_chunks")
        if os.path.exists(self.chunks_source_dir): shutil.rmtree(self.chunks_source_dir)
        os.makedirs(self.chunks_source_dir)

        self._update_status(f"Dosya parçalara ayrılıyor...\nHedef: {self.chunks_source_dir}\n\n", "info")
        md5_total, sha256_total, sha512_total = hashlib.md5(), hashlib.sha256(), hashlib.sha512()

        for index, chunk in self._split_file_generator(self.filepath):
            self._update_status(f"--- Parça {index} Hash'i ---\n", "bold")
            self._update_status(f"  MD5: {hashlib.md5(chunk).hexdigest()}\n")
            self._update_status(f"  SHA256: {hashlib.sha256(chunk).hexdigest()}\n")
            self._update_status(f"  SHA512: {hashlib.sha512(chunk).hexdigest()}\n")
            chunk_filename = os.path.join(self.chunks_source_dir, f"chunk_{index}")
            with open(chunk_filename, "wb") as f:
                f.write(chunk)
            md5_total.update(chunk)
            sha256_total.update(chunk)
            sha512_total.update(chunk)

        self.original_hashes = {'md5': md5_total.hexdigest(), 'sha256': sha256_total.hexdigest(), 'sha512': sha512_total.hexdigest()}
        self._update_status("\n--- TÜM DOSYANIN ORİJİNAL HASHI ---\n", "bold")
        self._update_status(f"MD5:    {self.original_hashes['md5']}\nSHA256: {self.original_hashes['sha256']}\nSHA512: {self.original_hashes['sha512']}\n")
        self.file_label.config(text=f"Seçili: {os.path.basename(self.filepath)}")
        messagebox.showinfo("Başarılı", "Hash hesaplama ve parçalara ayırma tamamlandı.")

    def encrypt_all(self):
       
        if not self.filepath:
            messagebox.showwarning("Uyarı", "Lütfen önce 1. adımı çalıştırarak bir dosya seçin.")
            return

        recipient = simpledialog.askstring("PGP Şifreleme", "Alıcının PGP Anahtar ID'sini veya E-postasını girin:")
        if not recipient: return
        
        self._update_status("\n--- Bütün Dosya Şifreleniyor ---\n", "bold")
        encrypted_filepath = self.filepath + ".gpg"
        try:
            with open(self.filepath, 'rb') as f:
                status = self.gpg.encrypt_file(f, recipients=[recipient], output=encrypted_filepath, always_trust=True)
            if status.ok: self._update_status(f"Başarılı: {encrypted_filepath}\n", "success")
            else: self._update_status(f"Hata: {status.stderr}\n", "error")
        except Exception as e: self._update_status(f"Kritik Hata: {e}\n", "error")

        if not self.chunks_source_dir or not os.path.exists(self.chunks_source_dir):
            messagebox.showwarning("Uyarı", "Parça klasörü bulunamadı.")
            return

        self._update_status("\n--- Parçalar Şifreleniyor ---\n", "bold")
        encrypted_chunks_dir = self.chunks_source_dir.replace("_chunks", "_encrypted_chunks")
        if os.path.exists(encrypted_chunks_dir): shutil.rmtree(encrypted_chunks_dir)
        os.makedirs(encrypted_chunks_dir)

        for filename in sorted(os.listdir(self.chunks_source_dir), key=lambda x: int(x.split('_')[-1])):
            chunk_path = os.path.join(self.chunks_source_dir, filename)
            encrypted_chunk_path = os.path.join(encrypted_chunks_dir, filename + ".gpg")
            with open(chunk_path, "rb") as f:
                status = self.gpg.encrypt_file(f, recipients=[recipient], output=encrypted_chunk_path, always_trust=True)
            if status.ok: self._update_status(f"Parça şifrelendi: {filename}.gpg\n", "success")
            else: self._update_status(f"Parça şifreleme hatası ({filename}): {status.stderr}\n", "error")
        
        messagebox.showinfo("Tamamlandı", "Bütün dosya ve tüm parçalar şifrelendi.")

    def show_decrypt_options(self):
        
        dialog = Toplevel(self.root)
        dialog.title("Şifre Çözme Seçeneği")
        dialog.geometry("350x150")
        tk.Label(dialog, text="Hangi işlemi yapmak istiyorsunuz?", font=('Helvetica', 12)).pack(pady=20)
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Tek Dosya Çöz", command=lambda: [dialog.destroy(), self._decrypt_single_file()]).pack(side=tk.LEFT, padx=10, ipady=5)
        Button(btn_frame, text="Parça Klasörü Çöz", command=lambda: [dialog.destroy(), self._decrypt_chunks_folder()]).pack(side=tk.LEFT, padx=10, ipady=5)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
    
    

    def _perform_integrity_check(self, filepath_to_check):
        """Verilen dosyanın hash'lerini hesaplar ve orijinaliyle karşılaştırır."""
        if not self.original_hashes:
            self._update_status("\nBÜTÜNLÜK KONTROLÜ ATLANDI: Orijinal hash değerleri bulunamadı.\n", "error")
            return False

        self._update_status("\n--- BÜTÜNLÜK KONTROLÜ BAŞLATILDI ---\n", "bold")
        self._update_status(f"Kontrol edilen dosya: {os.path.basename(filepath_to_check)}\n")

        md5_new, sha256_new, sha512_new = hashlib.md5(), hashlib.sha256(), hashlib.sha512()
        try:
            with open(filepath_to_check, 'rb') as f:
                while chunk := f.read(4096 * 1024):  # 4MB'lık bloklar halinde oku
                    md5_new.update(chunk)
                    sha256_new.update(chunk)
                    sha512_new.update(chunk)
        except FileNotFoundError:
             self._update_status(f"HATA: Bütünlük kontrolü için {filepath_to_check} dosyası bulunamadı.\n", "error")
             return False

        new_hashes = {'md5': md5_new.hexdigest(), 'sha256': sha256_new.hexdigest(), 'sha512': sha512_new.hexdigest()}

        self._update_status("Orijinal Hash'ler:\n", 'info')
        for algo, h in self.original_hashes.items(): self._update_status(f"  {algo.upper()}: {h}\n")
        
        self._update_status("Yeni Hesaplanan Hash'ler:\n", 'info')
        for algo, h in new_hashes.items(): self._update_status(f"  {algo.upper()}: {h}\n")

        all_match = (self.original_hashes['md5'] == new_hashes['md5'] and
                     self.original_hashes['sha256'] == new_hashes['sha256'] and
                     self.original_hashes['sha512'] == new_hashes['sha512'])

        if all_match:
            self._update_status("\nSONUÇ: BAŞARILI! Tüm hash değerleri eşleşiyor. Bütünlük doğrulandı.\n", "success")
        else:
            self._update_status("\nSONUÇ: BAŞARISIZ! Hash değerleri EŞLEŞMİYOR!\n", "error")
        return all_match

    def _decrypt_single_file(self):
        encrypted_filepath = filedialog.askopenfilename(title="Şifreli Bütün Dosyayı Seçin", filetypes=[("GPG Dosyaları", "*.gpg;*.asc")])
        if not encrypted_filepath: return
        
        passphrase = simpledialog.askstring("PGP Parolası", "Özel anahtarınızın parolasını girin (varsa):", show='*')
        decrypted_filepath, _ = os.path.splitext(encrypted_filepath)
        if os.path.exists(decrypted_filepath):
             base, ext = os.path.splitext(decrypted_filepath)
             decrypted_filepath = f"{base}_decrypted{ext}"
        try:
            with open(encrypted_filepath, 'rb') as f:
                status = self.gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_filepath)
            
            if status.ok:
                self._update_status(f"\nDosyanın şifresi çözüldü: {os.path.basename(decrypted_filepath)}\n", "success")
                if self._perform_integrity_check(decrypted_filepath):
                    messagebox.showinfo("Başarılı", "Dosyanın şifresi çözüldü ve BÜTÜNLÜK DOĞRULANDI.")
                else:
                    messagebox.showwarning("Bütünlük Hatası", "Dosyanın şifresi çözüldü ancak bütünlüğü doğrulanamadı!")
            else:
                self._update_status(f"Şifre çözme hatası: {status.stderr}\n", "error")
        except Exception as e:
            self._update_status(f"Kritik hata: {e}\n", "error")

    def _decrypt_chunks_folder(self):
        encrypted_chunks_dir = filedialog.askdirectory(title="Şifreli Parçaların Bulunduğu Klasörü Seçin")
        if not encrypted_chunks_dir: return
        
        passphrase = simpledialog.askstring("PGP Parolası", "Özel anahtarınızın parolasını girin (varsa):", show='*')
        decrypted_chunks_dir = encrypted_chunks_dir.replace("_encrypted", "_decrypted")
        if os.path.exists(decrypted_chunks_dir): shutil.rmtree(decrypted_chunks_dir)
        os.makedirs(decrypted_chunks_dir)
        self._update_status("\n--- Parçaların Şifresi Çözülüyor ---\n", "bold")

        for filename in sorted(os.listdir(encrypted_chunks_dir), key=lambda x: int(x.split('_')[-1].split('.')[0])):
            if filename.endswith(".gpg"):
                encrypted_path = os.path.join(encrypted_chunks_dir, filename)
                decrypted_path = os.path.join(decrypted_chunks_dir, filename.replace(".gpg", ""))
                with open(encrypted_path, "rb") as f: status = self.gpg.decrypt_file(f, passphrase=passphrase, output=decrypted_path)
                if status.ok: self._update_status(f"Çözüldü: {filename}\n", "success")
                else: self._update_status(f"Hata ({filename}): {status.stderr}\n", "error")
        
        self._update_status("\n--- Parçalar Birleştiriliyor ---\n", "bold")
        # Orijinal dosya uzantısını korumaya çalış
        original_ext = os.path.splitext(self.filepath or "file.bin")[-1]
        reassembled_file_path = os.path.join(os.path.dirname(decrypted_chunks_dir), f"reassembled_file{original_ext}")

        try:
            with open(reassembled_file_path, "wb") as outfile:
                chunk_files = sorted(os.listdir(decrypted_chunks_dir), key=lambda x: int(x.split('_')[-1]))
                for filename in chunk_files:
                    with open(os.path.join(decrypted_chunks_dir, filename), "rb") as infile:
                        outfile.write(infile.read())
            
            self._update_status(f"Dosya başarıyla birleştirildi: {os.path.basename(reassembled_file_path)}\n", "success")
            
            # Birleştirilmiş dosya üzerinde bütünlük kontrolü yap
            if self._perform_integrity_check(reassembled_file_path):
                messagebox.showinfo("Tamamlandı", "Tüm parçalar çözüldü, dosya birleştirildi ve BÜTÜNLÜK DOĞRULANDI.")
            else:
                messagebox.showwarning("Bütünlük Hatası", "Parçalar birleştirildi ancak orijinal dosya ile hash'leri eşleşmiyor!")
        except Exception as e:
            self._update_status(f"Birleştirme hatası: {e}\n", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileHasherApp(root)
    root.mainloop()