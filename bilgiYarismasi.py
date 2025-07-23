import pyodbc

def veritabaninaBaglan():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=EXCALIBUR\\SQLEXPRESS;' 
            'DATABASE=oyun1;'
            'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()
        return conn, cursor
    except pyodbc.Error as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None, None
    
global conn, cursor
conn, cursor = veritabaninaBaglan()
cursor.execute("SeLECT * FROM kullanicilar")
kullanicilar = cursor.fetchall()
print(f"kullanıcı bilgileri: {kullanicilar}")
alinanPuan = 0

def anaMenu(): 
    print("Merhaba " + kullaniciAdi + "\n\nOyuna başlamak için 1'e,\nAyarlar için 2'ye,\nOyundan çıkmak için 3'e basın:")
    girilenDeger = int(input())
    if girilenDeger == 1:
        oyun()
    elif girilenDeger == 2:
        ayarlar()
    elif girilenDeger == 3:
        cikis()  
    else:
        print("Geçersiz giriş! Lütfen 1, 2 veya 3 girin.")

def oyun():
    print("Bilgi Yarışması Başladı")
    soruGetir()

def soruGetir():
    try:
        cursor.execute("SELECT TOP 10 * FROM sorular ORDER BY NEWID()")
        sorular = cursor.fetchall()
        if not sorular:
            print("Veritabanında soru bulunamadı.")
            return

        for sayac, soru in enumerate(sorular, 1):
            print(f"\nSoru {sayac}: {soru.soru}")
            print("1) " + soru.scvp1)
            print("2) " + soru.scvp2)
            print("3) " + soru.scvp3)
            print("4) " + soru.scvp4)
            cevapKontrol(soru)

        sonuc()

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        return


def cevapKontrol(soru):
    global alinanPuan
    print("Cevabınızı girin:")
    girilenCevap = input().strip()

    if girilenCevap == str(soru.cevap):
        alinanPuan += 10
        print("✅ Tebrikler! Doğru cevap verdiniz.")
    else:
        alinanPuan -= 5
        print("❌ Üzgünüz, yanlış cevap verdiniz.")
def sonuc():
    global alinanPuan
    cursor.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", kullaniciAdi)
    kullanici = cursor.fetchone()

    if kullanici is None:
        print("Kullanıcı bulunamadı.")
        return

    puan = kullanici.puan
    seviye = kullanici.seviye

    yeniPuan = puan + alinanPuan

    if (puan % 100 + alinanPuan) >= 100:
        seviye += 1
        print(f"🎉 Tebrikler! Seviye atladınız! Yeni seviyeniz: {seviye}")

    print(f"Oyun bitti, toplam puanınız: {yeniPuan}")

    cursor.execute(
        "UPDATE kullanicilar SET puan = ?, seviye = ? WHERE kullaniciAdi = ?",
        (yeniPuan, seviye, kullaniciAdi)
    )
    conn.commit()

    alinanPuan = 0
    anaMenu()

def ayarlar():
    while True:
        print("Ayarlara Hoşgeldiniz! \n\nKullanıcı adı değiştirmek için 1'e, \nBilgilerinizi görmek için 2'ye, \nAyarlardan çıkmak için 3'e basın:")
        try:
            girilenDeger = int(input())
        except ValueError:
            print("Lütfen sadece sayı girin!")
            continue

        if girilenDeger == 1:
            kullaniciAdiDegistir()
        elif girilenDeger == 2:
            bilgileriGoruntule()
        elif girilenDeger == 3:
            print("Ayarlar menüsünden çıkılıyor...")
            anaMenu()
        else:
            print("Geçersiz giriş! Lütfen 1, 2 veya 3 girin.")

def kullaniciAdiDegistir():
    global kullaniciAdi
    print("Yeni kullanıcı adınızı girin:")
    yeniKullaniciAdi = input().strip()

    cursor.execute("UPDATE kullanicilar SET kullaniciAdi = ? WHERE kullaniciAdi = ?", (yeniKullaniciAdi, kullaniciAdi))
    conn.commit()

    kullaniciAdi = yeniKullaniciAdi
    print("Kullanıcı adınız başarıyla değiştirildi!")

def bilgileriGoruntule():

    cursor.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", kullaniciAdi)
    kullanici = cursor.fetchone()

    if kullanici is None:
        print("Kullanıcı bilgileri bulunamadı.")
        return

    puan = kullanici.puan
    seviye = kullanici.seviye

    print(f"Kullanıcı Adı: {kullaniciAdi} \nSeviyeniz: {seviye} \nPuanınız: {puan}")

def cikis():
    print("Oyundan çıkılıyor...")
    exit()

print("🎮 Oyuna hoş geldiniz!\nLütfen kullanıcı adınızı girin:")
global kullaniciAdi
kullaniciAdi = input().strip()

cursor.execute("SELECT * FROM kullanicilar WHERE kullaniciAdi = ?", kullaniciAdi)
kullanici = cursor.fetchone()

if kullanici is None:

    print(f"🆕 '{kullaniciAdi}' adına yeni bir kullanıcı oluşturuluyor...")
    cursor.execute(
        "INSERT INTO kullanicilar (kullaniciAdi, puan, seviye) VALUES (?, ?, ?)",
        (kullaniciAdi, 0, 1)  
    )
    conn.commit()
    print(f"✅ Kayıt başarılı! Hoş geldin, {kullaniciAdi}!")
else:
    print(f"✅ Hoş geldin tekrar, {kullaniciAdi}! Seviyen: {kullanici.seviye}, Puanın: {kullanici.puan}")


anaMenu()

