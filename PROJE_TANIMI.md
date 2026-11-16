============================================================

PROJE GENEL TANIMI VE KURALLARI

============================================================

\- Yukarıda detayı verilen her tablo için bir CRUD işlemleri yapan bir API servisi oluşturulacaktır.

\- Tüm mesaj ve uyarılar Türkçe olacaktır.

\- Giriş ekranında USERNAME olarak girilen değer, tüm ekranlarda yeni kayıt oluşturulduğunda otomatik olarak CREATED\_BY alanına atanacaktır; güncelleme ve silme işlemlerinde bu alanda değişiklik yapılmayacaktır.



\------------------------------------------------------------

1\. USERSINS TABLOSU VE İŞ KURALLARI

\------------------------------------------------------------

\- USERNAME alanı primary (birincil) bir alan olacaktır.

\- Arama işlemi USERNAME veya FULL\_NAME ile yapılabilecektir.

\- PASSWORD\_HASH alanı yeni bir kayıt oluşturulduğunda ya da güncelleme yapıldığında kuvvetli bir hash fonksiyonundan geçirilerek veritabanına kaydedilecektir.

\- USERNAME, PASSWORD\_HASH, FULL\_NAME, EMAIL, ROLE alanları girilmesi zorunlu alanlar olacaktır.



Tablo Şeması (usersins):

\- USERNAME      : NOT NULL VARCHAR2(20)

\- PASSWORD\_HASH : NOT NULL VARCHAR2(255)

\- FULL\_NAME     : NOT NULL VARCHAR2(100)

\- EMAIL         : NOT NULL VARCHAR2(100)

\- ROLE          :          VARCHAR2(20)

\- IS\_ACTIVE     :          NUMBER(1)

\- CREATED\_AT    :          TIMESTAMP(6)

\- UPDATED\_AT    :          TIMESTAMP(6)



\------------------------------------------------------------

2\. PRODUCT\_TYPES TABLOSU

\------------------------------------------------------------

Tablo Şeması (product\_types):

\- PRODUCT\_TYPE  : NOT NULL VARCHAR2(5)

\- PRODUCT\_NAME  : NOT NULL VARCHAR2(50)



\------------------------------------------------------------

3\. POLICIES TABLOSU VE İŞ KURALLARI

\------------------------------------------------------------

Tablo Şeması (policies):

\- POLICY\_ID     : NOT NULL NUMBER

\- POLICY\_NO     :          VARCHAR2(30)

\- TCKN\_VKN      : NOT NULL VARCHAR2(11)

\- PRODUCT\_TYPE  : NOT NULL VARCHAR2(5)

\- START\_DATE    : NOT NULL DATE

\- END\_DATE      : NOT NULL DATE

\- PREMIUM\_AMOUNT: NOT NULL NUMBER(15,2)

\- STATUS        :          VARCHAR2(20)

\- CREATED\_BY    :          VARCHAR2(20)

\- CREATED\_AT    :          TIMESTAMP(6)



\------------------------------------------------------------

4\. CUSTOMERS TABLOSU

\------------------------------------------------------------

Tablo Şeması (customers):

\- TCKN\_VKN      : NOT NULL VARCHAR2(11)

\- FIRST\_NAME    : NOT NULL VARCHAR2(50)

\- LAST\_NAME     : NOT NULL VARCHAR2(50)

\- EMAIL         :          VARCHAR2(100)

\- PHONE         : NOT NULL VARCHAR2(20)

\- BIRTH\_DATE    :          DATE

\- GENDER        :          CHAR(1)

\- ADDRESS       :          VARCHAR2(500)

\- CREATED\_BY    :          VARCHAR2(20)

\- CREATED\_AT    :          TIMESTAMP(6)



\------------------------------------------------------------

5\. CLAIMS TABLOSU

\------------------------------------------------------------

Tablo Şeması (claims):

\- CLAIM\_ID      : NOT NULL NUMBER

\- CLAIM\_NO      : NOT NULL VARCHAR2(30)

\- POLICY\_ID     : NOT NULL NUMBER

\- INCIDENT\_DATE : NOT NULL DATE

\- CLAIM\_DATE    : NOT NULL DATE

\- CLAIM\_AMOUNT  : NOT NULL NUMBER(15,2)

\- PAID\_AMOUNT   :          NUMBER(15,2)

\- STATUS        :          VARCHAR2(20)

\- DESCRIPTION   :          VARCHAR2(1000)

\- CREATED\_BY    :          VARCHAR2(20)

\- CREATED\_AT    :          TIMESTAMP(6)



============================================================

EKRAN VE ARAYÜZ KURALLARI

============================================================



1\. GİRİŞ EKRANI:

\- usersins tablosunda yer alan kullanıcı adı ve şifresi doğru ise programa girişe izin verilecektir.

\- Şifre alanı yıldızla maskelenecek, istenirse kullanıcı bunu görebilecektir.

\- Kullanıcı usersins tablosunda yoksa ve yeni bir kullanıcı ise yeni kayıt oluşturabilecektir.

\- Kullanıcı adı ve şifre doğru ise program açılacak ve ana menü gelecektir.



2\. ANA MENÜ VE CRUD EKRANLARI:

\- Menüde; usersins, customer, product\_types, policies ve claims tabloları üzerinde yeni kayıt ekleme, kayıt güncelleme, kayıt silme ve kayıt sorgulama işlemleri yapabilen şık bir ekran yer alacaktır.

\- Tüm alanların validasyonlarına dikkat edilecek ve hatalı işlemlerde yapılan hata mesajı Türkçe olarak ekranda gösterilecektir.



3\. CUSTOMER EKRANI:

\- GENDER (Cinsiyet) alanı: Erkek = E, Kadın = K, Belirtmek istemiyor = X şeklinde bir listbox üzerinden seçilecektir.

\- BIRTH\_DATE (Doğum Tarihi): Bir takvim (calendar) üzerinden seçilebilecek, kullanıcı isterse gün/ay/yıl şeklinde elle de girebilecektir.



4\. POLICIES EKRANI:

\- TCKN\_VKN elle doldurulabilecektir.

\- Girilen TCKN\_VKN'ye ait bir kayıt customer tablosunda varsa; bu değere ait TCKN\_VKN, FIRST\_NAME, LAST\_NAME, EMAIL, BIRTH\_DATE alanları ekranda uygun bir şekilde gösterilecek ve bu alanlar düzenlenemeyecektir (edit edilemeyecek).

\- TCKN\_VKN'ye ait bir kayıt customer tablosunda yoksa "müşteri bulunmadı" hatası verilecektir.

\- TCKN\_VKN alanının yanında bir buton bulunacak; bu butona basıldığında müşteri tablosu üzerinde arama yapılabilen, kayıt bulunduğunda ve onaylandığında ilgili TCKN\_VKN'yi dolduran küçük bir arama ekranı açılacaktır. Bu ekranda sadece sorgulamaya izin veren TCKN\_VKN, FIRST\_NAME, LAST\_NAME, EMAIL, BIRTH\_DATE alanları yer alacaktır.

\- PRODUCT\_TYPE alanı bir listbox olacak ve product\_types tablosundan seçilecektir.

\- START\_DATE ve END\_DATE alanları bir takvim (calendar) üzerinden seçilebilecek, kullanıcı isterse elle de girebilecektir.



5\. CLAIMS EKRANI:

\- POLICY\_ID elle girilebilecektir. Bu alana girilen değer policies tablosunda varsa, o poliçeye ait POLICY\_NO ve diğer tüm bilgiler ekranda uygun bir şekilde gösterilecek ve düzenlenemeyecektir (edit edilemeyecek).

\- Eğer girilen değer policies tablosunda yoksa "poliçe bulunamadı" mesajı verilecektir.

\- POLICY\_ID alanının yanında bir "poliçe bul" butonu olacak; tıklandığında arama penceresi açılacaktır. Bu pencerede policies tablosu üzerinde TCKN\_VKN, PRODUCT\_TYPE, START\_DATE, END\_DATE ve STATUS alanları ile arama yapılabilecektir.

\- Bir kayıt seçildiğinde o kayda ait POLICY\_ID, claim ekranı üzerindeki POLICY\_ID alanına atanacaktır. Doğru bir POLICY\_ID seçildiğinde poliçenin sahibi olan müşterinin bilgileri de düzenlenemez (read-only) şekilde ekranda gösterilecektir. Müşteri bilgilerinde sadece TCKN\_VKN, FIRST\_NAME, LAST\_NAME, EMAIL, BIRTH\_DATE alanları yer alacaktır.

\- INCIDENT\_DATE ve CLAIM\_DATE alanları bir takvim (calendar) üzerinden seçilebilecek, kullanıcı isterse elle de girebilecektir.



\------ sonradan EKLENENLER.

PROJEYE REPAIR\_PARTS adında bir tablo ekledim.



Name            Null?    Type          

\--------------- -------- ------------- 

PART\_CODE       NOT NULL VARCHAR2(50)  

PART\_NAME       NOT NULL VARCHAR2(150) 

WARRANTY\_MONTHS          NUMBER(3)     

UNIT\_PRICE      NOT NULL NUMBER(12,2)  

LABOR\_PRICE     NOT NULL NUMBER(12,2)  

ORIGIN\_COUNTRY           VARCHAR2(50)  

CREATED\_BY               VARCHAR2(20)  

CREATED\_DATE             TIMESTAMP(6) 





tablo üzerinde yeni kayıt ekleme, kayıt güncelleme, kayıt silme ve kayıt sorgulama işlemleri yapabilen şık bir ekran yer alacaktır.

\- Tüm alanların validasyonlarına dikkat edilecek ve hatalı işlemlerde yapılan hata mesajı Türkçe olarak ekranda gösterilecektir. bununla ilgili servisleri ve arayüzü oluştur. CREATED\_BY alanı giriş ekranından alınan USERNAME değeri olacaktır.



