import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from journal.models import (
    YearCategory, Journal, Category, Article, Editorial, 
    SocialMedia, SitePage, SendingArticle, About
)
from users.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data for Surxondaryo: Ilm va Tafakkur journal.'

    def _create_placeholder_image(self):
        # Create a tiny 1x1 GIF
        gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        )
        return SimpleUploadedFile("placeholder.gif", gif, content_type="image/gif")
        
    def _create_placeholder_pdf(self):
        # Create a dummy PDF file content
        pdf_content = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%EOF\n"
        return SimpleUploadedFile("dummy.pdf", pdf_content, content_type="application/pdf")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting to populate sample data..."))

        # 1. Superuser
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@surxon.uz',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Superuser created.'))
        else:
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['is_staff', 'is_superuser'])
            self.stdout.write(self.style.WARNING('Superuser already exists, updated permissions.'))
        Profile.objects.update_or_create(user=user, defaults={'is_admin': True})

        # 2. About
        if not About.objects.exists():
            about_content = """
            <p><strong>"Surxondaryo: Ilm va Tafakkur"</strong> ilmiy jurnali voha hududida fan va ta'limni rivojlantirish, yosh olimlar va tadqiqotchilarning ilmiy ishlarini ommalashtirish maqsadida tashkil etilgan.</p>
            <p>Jurnalimizda ijtimoiy-gumanitar, aniq va tabiiy fanlar sohasidagi eng so'nggi yutuqlar, ilmiy yangiliklar va innovatsion g'oyalar yoritib boriladi. Bizning maqsadimiz ilmiy hamjamiyatni birlashtirish va O'zbekiston ilm-fanini xalqaro darajaga olib chiqishdir.</p>
            <p>Ushbu nashr O'zbekiston Respublikasi Oliy Attestatsiya Komissiyasi (OAK) talablariga to'liq javob beradi va barcha yo'nalishlar bo'yicha ilmiy maqolalarni qabul qiladi.</p>
            """
            
            author_desc = "<p>Tahririyat hay'ati vohaning yetakchi olimlari va soha mutaxassislaridan iborat. Biz har bir maqolani xolis va chuqur tahlil qilib, sifatli kontent taqdim etishga intilamiz.</p>"
            
            about = About(
                journal_name='Surxondaryo: Ilm va Tafakkur',
                content=about_content,
                author_description=author_desc,
            )
            about.journal_image = self._create_placeholder_image()
            about.author_image = self._create_placeholder_image()
            about.save()
            self.stdout.write(self.style.SUCCESS('About page created.'))
        else:
            self.stdout.write(self.style.WARNING('About page already exists.'))

        # 3. YearCategory
        years = [2024, 2025, 2026]
        year_objs = {}
        for y in years:
            obj, c = YearCategory.objects.get_or_create(year=y)
            year_objs[y] = obj
        self.stdout.write(self.style.SUCCESS('Year categories created.'))

        # 4. Journal
        journals_list = []
        for y in years:
            for num in [1, 2, 3]:
                j, c = Journal.objects.get_or_create(
                    year_category=year_objs[y],
                    source_number=num
                )
                if c:
                    j.image = self._create_placeholder_image()
                    j.file = self._create_placeholder_pdf()
                    j.save()
                journals_list.append(j)
        self.stdout.write(self.style.SUCCESS(f'{len(journals_list)} Journals created/verified.'))

        # 5. Category
        categories_data = [
            ("Falsafa fanlari", "#1b3a6b"),
            ("Tarix fanlari", "#8b0000"),
            ("Filologiya fanlari", "#228b22"),
            ("Pedagogika fanlari", "#ff8c00"),
            ("Huquq fanlari", "#4b0082"),
            ("Iqtisodiyot fanlari", "#008080")
        ]
        category_objs = []
        for name, color in categories_data:
            cat, c = Category.objects.get_or_create(name=name, defaults={'color': color})
            category_objs.append(cat)
        self.stdout.write(self.style.SUCCESS('Categories created.'))

        # 6. Article
        authors = ['Karimov A.B.', 'Raximova S.T.', 'Toshmatov O.Q.', 'Eshmatova N.A.', 'Soliyev Q.W.', 'Nazarov D.E.']
        abstract_tmpl = "<p>Ushbu maqolada sohaga oid dolzarb muammolar tahlil qilingan. Xususan, O'zbekiston sharoitida olib borilayotgan islohotlar va ularning natijalari ilmiy asoslangan. Olingan xulosalar va berilgan tavsiyalar amaliy ahamiyatga ega. Kelgusidagi tadqiqotlar uchun ushbu ish muhim manba bo'lib xizmat qilishi mumkin.</p>"
        
        article_titles = [
            # Falsafa
            "JAMIYAT TARAQQIYOTIDA MILLIY G'OYANING ROLI", "GLOBALLASHUV JARAYONIDA YOSHLAR MA'NAVIYATI", "SHARQ MUTAFAKKIRLARI MEROSIDA AXLOQIY QADRIYATLAR", "AXBOROT LASHUVI DAVRIDA INSON ONGINING O'ZGARISHI", "KONTSEPTUAL FALSAFANING BUGUNGI KUNDAGI AHAMIYATI", "MADANIYATLARARO MULOQOT: MUAMMO VA YECHIMLAR", "INSON HUQUQLARI FALSAFASI: ZAMONAVIY TALQIN",
            # Tarix
            "QADIMGI BAAQTRIA VA SOG'DIYONA: TARIXIY TAHLIL", "O'ZBEKISTON TARIXSHUNOSLIGIDA JADIDCHILIK HARAKATI", "AMIR TEMUR DAVLATINING MARKAZLASHUVI", "XIX ASR OXIRI - XX ASR BOSHIDA TURKISTON IQTISODIYOTI", "SURXONDARYO VILOYATI MODDIY MADANIYATI TARIXIDAN", "BUYUK IPAK YO'LINING MADANIY ALOQALARDAGI ROLI", "SOVET MUSTAMLAKACHILIGI DAVRIDA QISHLOQ XO'JALIGI",
            # Filologiya
            "ALISHER NAVOIY IJODIDA INSONPARVARLIK G'OYALARI", "ZAMONAVIY O'ZBEK ADABIY TILIDA LUG'AT BOYLASHUVI", "BADIIY ASAR TARJIMASIDA MUQOBILLIK MUAMMOSI", "FOLKLOR ASARLARIDA POETIK TIMSOLLAR", "QIYOSIY TILSHUNOSLIK: INGLIZ VA O'ZBEK TILLARI MISOLIDA", "JADID ADABIYOTI NAMANANDALARINING BADIIY MAHORATI", "TIL VA MADANIYAT MUTANOSIBLIGI",
            # Pedagogika
            "BOSHLANG'ICH TA'LIMDA ZAMONAVIY PEDAGOGIK TEXNOLOGIYALAR", "TALABALARDA KREATIVLIKNI RIVOJLANTIRISH YO'LLARI", "MASOFAVIY TA'LIMDA INTERAKTIV METODLARNING AHAMIYATI", "INKLYUZIV TA'LIMNI TASHKIL ETISHNING ASOSIY TAMOYILLARI", "MAKTABGACHA TA'LIMDA BOLALAR PSIXOLOGIYASI", "PEDAGOGIK MAHORAT: NAZARIYA VA AMALIYOT", "O'QUVCHILARDA BILISH FAOLIYATINI FAOLlashtirish",
            # Huquq
            "O'ZBEKISTON RESPUBLIKASIDA MA'MURIY HUQUQBUZARLIKLAR TIZIMI", "JINOYAT HUQUQIDA JAZONI YENGILLASHTIRUVCHI HOLATLAR", "FUQAROLIK HUQUQIDA SHARTNOMA MAJBURIYATLARI", "MEHNAT HUQUQIDA ISHCHILAR HUQUQLARINI HIMOYA QILISH", "XALQARO HUQUQ NORMALARINI MILLIY QONUNCHILIKKA IMPLEMENTATSIYA QILISH", "EKOLOGIYA HUQUQI: MUAMMO VA ISTIQBOLLAR", "KIBERJINOYATCHILIKKA QARSHI KURASHISHNING HUQUQIY ASOSLARI",
            # Iqtisodiyot
            "RAQAMLI IQTISODIYOTNI RIVOJLANTIRISHNING USTUVOR YO'NALISHLARI", "KICHIK BIZNES VA XUSUSIY TADBIRKORLIKNI QO'LLAB-QUVVATLASH", "INVESTITSIYA MUHITINI JALB QILISH: XORIJ TAJRIBASI", "QISHLOQ XO'JALIGIDA KLASTER TIZIMINING SAMARADORLIGI", "TIJORAT BANKLARIDA KREDIT TAVAKKALCHILIGINI BOSHQARISH", "INFLATSIYA JARAYONLARINI TARTIBGA SOLISH MEXANIZMLARI", "XIZMAT KO'RSATISH SOHASINI MODERNIZATSIYA QILISH"
        ]

        if not Article.objects.exists():
            art_idx = 0
            for j in journals_list:
                # ~4-5 articles per journal
                for _ in range(5):
                    if art_idx >= len(article_titles):
                        break
                    title = article_titles[art_idx]
                    category = category_objs[art_idx % len(category_objs)]
                    
                    year = j.year_category.year
                    issue = j.source_number
                    doi = f"https://doi.org/10.37547/surxon-{year}-{issue}-{art_idx+1}"
                    pages = f"{_ * 10 + 1}-{_ * 10 + 10}"
                    
                    article = Article(
                        title=title,
                        authors=authors[art_idx % len(authors)],
                        abstract=abstract_tmpl,
                        keywords="ilm-fan, jamiyat, taraqqiyot, innovatsiya, ta'lim",
                        doi=doi,
                        pages=pages,
                        journal=j,
                        category=category,
                        is_archived=False
                    )
                    article.pdf_file = self._create_placeholder_pdf()
                    article.save()
                    art_idx += 1
            self.stdout.write(self.style.SUCCESS(f'{art_idx} Articles created.'))
        else:
            self.stdout.write(self.style.WARNING('Articles already exist. Skipping.'))

        # 7. Editorial
        editorials_data = [
            ("Aziz", "Karimov", "Bosh muharrir"),
            ("Dilshod", "Rahmonov", "Muharrir"),
            ("Nigora", "Toshpulatova", "Tahrir hay'ati a'zosi"),
            ("Botir", "Xoliqov", "Tahrir hay'ati a'zosi"),
            ("Salima", "Jumayeva", "Ilmiy kotib"),
            ("Jasur", "Olimov", "Tahrir hay'ati a'zosi")
        ]
        for f, l, p in editorials_data:
            ed, c = Editorial.objects.get_or_create(first_name=f, last_name=l, defaults={'position': p})
            if c:
                ed.image = self._create_placeholder_image()
                ed.save()
        self.stdout.write(self.style.SUCCESS('Editorials created.'))

        # 8. SocialMedia
        SocialMedia.objects.get_or_create(
            title='telegram',
            defaults={
                'color': 'blue',
                'url': 'https://t.me/surxon_ilm_tafakkur'
            }
        )
        SocialMedia.objects.get_or_create(
            title='instagram',
            defaults={
                'color': 'red',
                'url': 'https://instagram.com/surxon_ilm_tafakkur'
            }
        )
        self.stdout.write(self.style.SUCCESS('Social Media created.'))

        # 9. SitePage
        SitePage.objects.get_or_create(
            page_type=SitePage.PageType.NASHR,
            defaults={
                'content': "<p>Jurnal nashr etiketkasi qoidalari Xalqaro nashriyot etikasi qo'mitasi (COPE) tavsiyalariga asoslanadi.</p><ul><li>Plagiatga yo'l qo'yilmaydi.</li><li>Mualliflar original tadqiqotlarni taqdim etishi shart.</li><li>Taqrizchilar xolisona baho berishi kerak.</li></ul>",
                'content_uz': "<p>Jurnal nashr etiketkasi qoidalari Xalqaro nashriyot etikasi qo'mitasi (COPE) tavsiyalariga asoslanadi.</p><ul><li>Plagiatga yo'l qo'yilmaydi.</li><li>Mualliflar original tadqiqotlarni taqdim etishi shart.</li><li>Taqrizchilar xolisona baho berishi kerak.</li></ul>",
            }
        )
        SitePage.objects.get_or_create(
            page_type=SitePage.PageType.MAXFIYLIK,
            defaults={
                'content': "<p>Ushbu saytda foydalanuvchilarning shaxsiy ma'lumotlari qat'iy sir saqlanadi va uchinchi shaxslarga berilmaydi. Sayt cookie fayllaridan faqat qulaylik maqsadida foydalanadi.</p>",
                'content_uz': "<p>Ushbu saytda foydalanuvchilarning shaxsiy ma'lumotlari qat'iy sir saqlanadi va uchinchi shaxslarga berilmaydi. Sayt cookie fayllaridan faqat qulaylik maqsadida foydalanadi.</p>",
            }
        )
        self.stdout.write(self.style.SUCCESS('Site Pages created.'))

        # 10. SendingArticle
        if not SendingArticle.objects.exists():
            SendingArticle.objects.create(
                content="""
                <h3>Maqola yuborish tartibi</h3>
                <p>Hurmatli mualliflar, maqolalaringizni quyidagi talablar asosida tayyorlab yuborishingizni so'raymiz:</p>
                <ol>
                    <li>Maqola hajmi: 5-15 bet (A4 format).</li>
                    <li>Shrift: Times New Roman, 14, qatorlar orasi 1.5.</li>
                    <li>Annotatsiya (O'zbek, Rus va Ingliz tillarida), 50-100 so'z.</li>
                    <li>Kalit so'zlar: kamida 5 ta.</li>
                    <li>Foydalanilgan adabiyotlar ro'yxati (APA uslubida).</li>
                </ol>
                <p>Maqolalar tahririyat tomonidan maxsus platforma yoki elektron pochta orqali qabul qilinadi va ko'rib chiqish muddati 10 kunni tashkil etadi.</p>
                """
            )
            self.stdout.write(self.style.SUCCESS('SendingArticle guide created.'))

        self.stdout.write(self.style.SUCCESS('Successfully populated sample data!'))
