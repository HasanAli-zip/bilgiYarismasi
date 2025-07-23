import pyodbc  # pyodbc kütüphanesi ile Python'dan SQL Server veritabanına bağlanmak için kullanılır.

# Veritabanına bağlanmayı sağlayan fonksiyon
def veritabaninaBaglan():
    try:
        # SQL Server'a bağlanmak için gerekli bağlantı bilgileri
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=Server Adınız;'  # SQL Server adını belirt
            'DATABASE=oyun1;'  # Kullanılacak veritabanı adı (verdiğim sorguda kullanılan veritabanı adı oyun1)
            'Trusted_Connection=yes;'  # Windows kimliği ile bağlanmak isterseniz
        )
        cursor = conn.cursor()  # SQL komutlarını çalıştırmak için cursor oluşturuluyor
        return conn, cursor  # Bağlantı ve cursor geri döndürülüyor
    except pyodbc.Error as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")  # Hata varsa ekrana yazdır
        return None, None  # Bağlantı başarısızsa boş dön

# Veritabanı bağlantısını başlatıyoruz
global conn, cursor
conn, cursor = veritabaninaBaglan()


alinanPuan = 0  # Oyuncunun bu oturumda kazandığı toplam puanı tutar

# Ana menüyü gösteren fonksiyon
def anaMenu(): 
    print("Merhaba " + kullaniciAdi + "\n\nOyuna başlamak için 1'e,\nAyarlar için 2'ye,\nOyundan çıkmak için 3'e basın:")
    girilenDeger = int(input())  # Kullanıcının menü seçimini al
    if girilenDeger == 1:
        oyun()  # Oyun başlat
    elif girilenDeger == 2:
        ayarlar()  # Ayarlar menüsüne git
    elif girilenDeger == 3:
        cikis()  # Programı kapat
    else:
        print("Geçersiz giriş! Lütfen 1, 2 veya 3 girin.")  # Hatalı giriş uyarısı

# Oyunu başlatan fonksiyon
def oyun():
    print("Bilgi Yarışması Başladı")
    soruGetir()  # Soruları getir ve oyunu başlat

# Veritabanından rastgele sorular çeker
def soruGetir():
    try:
        cursor.execute("SELECT TOP 10 * FROM sorular ORDER BY NEWID()")  # Rastgele 10 soru getir
        sorular = cursor.fetchall()
        if not sorular:
            print("Veritabanında soru bulunamadı.")
            return

        # Her bir soruyu kullanıcıya göster
        for sayac, soru in enumerate(sorular, 1):
            print(f"\nSoru {sayac}: {soru.soru}")
            print("1) " + soru.scvp1)
            print("2) " + soru.scvp2)
            print("3) " + soru.scvp3)
            print("4) " + soru.scvp4)
            cevapKontrol(soru)  # Cevabı kontrol et

        sonuc()  # Tüm sorular bittiğinde sonucu göster

    except Exception as e:
        print(f"Bir hata oluştu: {e}")  # Soru getirirken hata varsa yazdır
        return

# Kullanıcının verdiği cevabı kontrol eder
def cevapKontrol(soru):
    global alinanPuan
    print("Cevabınızı girin:")
    girilenCevap = input().strip()  # Kullanıcıdan cevap al

    if girilenCevap == str(soru.cevap):  # Doğruysa
        alinanPuan += 10  # 10 puan ekle
        print("Tebrikler! Doğru cevap verdiniz.")
    else:
        alinanPuan -= 5  # Yanlışsa 5 puan çıkar
        print("Üzgünüz, yanlış cevap verdiniz.")

# Oyun sonunda puan ve seviye güncellenir
def sonuc():
    global alinanPuan
    cursor.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", kullaniciAdi)
    kullanici = cursor.fetchone()  # Kullanıcı bilgilerini al

    if kullanici is None:
        print("Kullanıcı bulunamadı.")
        return

    puan = kullanici.puan
    seviye = kullanici.seviye
    yeniPuan = puan + alinanPuan  # Yeni puan hesaplanır

    # 100 puan barajı geçildiyse seviye atlat
    if (puan % 100 + alinanPuan) >= 100:
        seviye += 1
        print(f"Tebrikler! Seviye atladınız! Yeni seviyeniz: {seviye}")

    print(f"Oyun bitti, toplam puanınız: {yeniPuan}")

    # Veritabanında güncelleme yapılır
    cursor.execute(
        "UPDATE kullanicilar SET puan = ?, seviye = ? WHERE kullaniciAdi = ?",
        (yeniPuan, seviye, kullaniciAdi)
    )
    conn.commit()

    alinanPuan = 0  # Puan sıfırlanır
    anaMenu()  # Ana menüye geri dönülür

# Ayarlar menüsünü gösterir
def ayarlar():
    while True:
        print("Ayarlara Hoşgeldiniz! \n\nKullanıcı adı değiştirmek için 1'e, \nBilgilerinizi görmek için 2'ye, \nAyarlardan çıkmak için 3'e basın:")
        try:
            girilenDeger = int(input())  # Seçim al
        except ValueError:
            print("Lütfen sadece sayı girin!")  # Hatalı giriş uyarısı
            continue

        if girilenDeger == 1:
            kullaniciAdiDegistir()  # Kullanıcı adını değiştir
        elif girilenDeger == 2:
            bilgileriGoruntule()  # Bilgileri görüntüle
        elif girilenDeger == 3:
            print("Ayarlar menüsünden çıkılıyor...")
            anaMenu()  # Ana menüye dön
        else:
            print("Geçersiz giriş! Lütfen 1, 2 veya 3 girin.")

# Kullanıcı adını değiştiren fonksiyon
def kullaniciAdiDegistir():
    global kullaniciAdi
    print("Yeni kullanıcı adınızı girin:")
    yeniKullaniciAdi = input().strip()

    # Veritabanında kullanıcı adı güncellenir
    cursor.execute("UPDATE kullanicilar SET kullaniciAdi = ? WHERE kullaniciAdi = ?", (yeniKullaniciAdi, kullaniciAdi))
    conn.commit()

    kullaniciAdi = yeniKullaniciAdi  # Yeni ad bellekte de güncellenir
    print("Kullanıcı adınız başarıyla değiştirildi!")

# Kullanıcının bilgilerini gösterir
def bilgileriGoruntule():
    cursor.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", kullaniciAdi)
    kullanici = cursor.fetchone()

    if kullanici is None:
        print("Kullanıcı bilgileri bulunamadı.")
        return

    puan = kullanici.puan
    seviye = kullanici.seviye

    # Kullanıcıya mevcut bilgileri gösterilir
    print(f"Kullanıcı Adı: {kullaniciAdi} \nSeviyeniz: {seviye} \nPuanınız: {puan}")

# Oyunu kapatır
def cikis():
    print("Oyundan çıkılıyor...")
    exit()

# Program başladığında kullanıcıdan ad istenir
print("Oyuna hoş geldiniz!\nLütfen kullanıcı adınızı girin:")
global kullaniciAdi
kullaniciAdi = input().strip()

# Kullanıcı veritabanında var mı kontrol edilir
cursor.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", kullaniciAdi)
kullanici = cursor.fetchone()

# Yeni kullanıcıysa veritabanına eklenir
if kullanici is None:
    print(f"'{kullaniciAdi}' adına yeni bir kullanıcı oluşturuluyor...")
    cursor.execute(
        "INSERT INTO kullanicilar (kullaniciAdi, puan, seviye) VALUES (?, ?, ?)",
        (kullaniciAdi, 0, 1)
    )
    conn.commit()
    print(f"Kayıt başarılı! Hoş geldin, {kullaniciAdi}!")
else:
    # Var olan kullanıcıysa bilgileri gösterilir
    print(f"Hoş geldin tekrar, {kullaniciAdi}! Seviyen: {kullanici.seviye}, Puanın: {kullanici.puan}")

# Ana menüye yönlendirilir
anaMenu()
