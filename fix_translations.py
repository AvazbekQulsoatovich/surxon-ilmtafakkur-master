"""
Tarjima fayllarini tuzatuvchi skript.
- Yetishmayotgan matnlarni qo'shadi
- .mo fayllarni qayta kompilyatsiya qiladi
"""
import polib
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Barcha yangi tarjimalar ──────────────────────────────────────────────
# format: { 'uz_msgid': ('en_translation', 'ru_translation') }
TRANSLATIONS = {
    # Hero / umumiy
    'SURXONDARYO ILM VA TAFAKKUR':    ('SURXONDARYO: SCIENCE AND MIND', 'СУРХОНДАРЁ: НАУКА И МЫШЛЕНИЕ'),
    'ILMIY JURNAL':                   ('SCIENTIFIC JOURNAL',             'НАУЧНЫЙ ЖУРНАЛ'),
    'Ilmiy maqolalar va tadqiqotlar jurnali': (
        'Journal of Scientific Articles and Research',
        'Журнал научных статей и исследований'),
    'Surxon: Ilm va Tafakkur':        ('Surxondaryo: Science and Mind',  'Сурхондарё: Наука и Мышление'),

    # Qidiruv
    'Maqola, muallif yoki kalit so\'z qidiring...': (
        'Search articles, authors or keywords...',
        'Поиск статей, авторов или ключевых слов...'),
    'Qidirish':         ('Search',   'Поиск'),

    # Statistika
    'Maqola':           ('Article',  'Статья'),
    'Muallif':          ('Author',   'Автор'),
    "Ko'rishlar":       ('Views',    'Просмотры'),
    'Til':              ('Language', 'Язык'),

    # Indexlash
    'Indekslangan bazalar': ('Indexed Databases', 'Индексированные базы'),

    # Article list
    'Maqolalar kategoriyalari': ('Article Categories', 'Категории статей'),
    'Barcha maqolalar':         ('All Articles',       'Все статьи'),
    'Barcha kategoriyalar':     ('All Categories',     'Все категории'),
    'Barcha kategoriyalarga qaytish': ('Back to all categories', 'Вернуться ко всем категориям'),
    'Kategoriyalar':            ('Categories',         'Категории'),
    'ta maqola':                ('articles',           'статей'),

    # Bands / Bo'limlar
    'Band qo\'shish':   ('Add Section',    'Добавить раздел'),
    'Saqlash':          ('Save',           'Сохранить'),
    "Bo'limni o'chirish": ('Delete Section', 'Удалить раздел'),
    'Matn kiriting...': ('Enter text...',  'Введите текст...'),
    'Band sarlavhasi':  ('Section title',  'Заголовок раздела'),

    # Archive / Arxiv
    'Arxiv':                    ('Archive',           'Архив'),
    'Arxivlangan maqolalar':    ('Archived Articles', 'Архивированные статьи'),
    'ta jurnal':                ('journals',           'журналов'),
    'Arxivdan chiqar':          ('Unarchive',          'Из архива'),
    'Arxivga':                  ('Archive',            'В архив'),
    'Arxivda':                  ('Archived',           'В архиве'),

    # Navbar / Footer
    'Bosh sahifa':      ('Home',          'Главная'),
    'Sahifalar':        ('Pages',         'Страницы'),
    'Jurnal':           ('Journal',       'Журнал'),
    'Jurnal haqida':    ('About Journal', 'О журнале'),
    'Tahrir hay\'ati':  ('Editorial Board', 'Редколлегия'),
    'Maqola yuborish':  ('Submit Article', 'Отправить статью'),
    'Aloqa':            ('Contact',        'Контакт'),
    'Yangiliklar':      ('News',           'Новости'),
    "Ishlab chiquvchi:": ('Developer:', 'Разработчик:'),
    "Barcha huquqlar himoyalangan.": (
        'All rights reserved.', 'Все права защищены.'),
    'Django bilan qurilgan': ('Built with Django', 'Создано на Django'),

    # Footer desc
    "Surxondaryo viloyatidagi ilmiy tadqiqotlar va maqolalar jurnali. Ilm-fan va tafakkurni rivojlantirishga hissa qo'shamiz.": (
        "A journal of scientific research and articles in Surxondaryo region. We contribute to the development of science and knowledge.",
        "Журнал научных исследований и статей Сурхандарьинской области. Вносим вклад в развитие науки и знаний."),
    "Surxondaryo viloyati, O'zbekiston": (
        "Surxondaryo region, Uzbekistan",
        "Сурхандарьинская область, Узбекистан"),

    # Auth
    "Kirish":           ('Login',    'Войти'),
    "Chiqish":          ('Logout',   'Выйти'),
    "Ro'yxatdan o'tish": ('Register', 'Регистрация'),
    "Profil":           ('Profile',  'Профиль'),

    # Pagination / misc
    'oldin':            ('ago',      'назад'),
    'ta':               ('',         ''),
    'Batafsil':         ('Read more','Подробнее'),
    "Ko'rish":          ('View',     'Просмотр'),
    'Tahrirlash':       ('Edit',     'Редактировать'),
    "O'chirish":        ('Delete',   'Удалить'),
    'Yaratish':         ('Create',   'Создать'),

    # Article detail
    "Ko'rishlar soni: ": ('Number of views: ', 'Количество просмотров: '),
    'Mualliflar:':       ('Authors:',           'Авторы:'),
    'Kategoriya:':       ('Category:',          'Категория:'),
    'Sana:':             ('Date:',              'Дата:'),

    # Contact
    "Biz bilan bog'lanish": ('Contact Us', 'Свяжитесь с нами'),
    "Ism":       ('Name',    'Имя'),
    "Xabar":     ('Message', 'Сообщение'),
    "Yuborish":  ('Send',    'Отправить'),

    # Months (used in archive)
    'Yanvar':    ('January',   'Январь'),
    'Fevral':    ('February',  'Февраль'),
    'Mart':      ('March',     'Март'),
    'Aprel':     ('April',     'Апрель'),
    'May':       ('May',       'Май'),
    'Iyun':      ('June',      'Июнь'),
    'Iyul':      ('July',      'Июль'),
    'Avgust':    ('August',    'Август'),
    'Sentabr':   ('September', 'Сентябрь'),
    'Oktabr':    ('October',   'Октябрь'),
    'Noyabr':    ('November',  'Ноябрь'),
    'Dekabr':    ('December',  'Декабрь'),

    # Tashkil
    'Tashkil etilgan': ('Founded',  'Основан'),

    # Language names
    'Uzbek':   ('Uzbek',   'Узбекский'),
    'English': ('English', 'Английский'),
    'Russian': ('Russian', 'Русский'),

    # ── Admin sidebar ──────────────────────────────────────
    'Super Admin':              ('Super Admin',               'Супер Администратор'),
    'Admin':                    ('Admin',                     'Администратор'),
    'Sahifalar':                ('Pages',                     'Страницы'),
    'Bosh sahifa':              ('Home',                      'Главная'),
    'Tahririyat':               ('Editorial',                 'Редакция'),
    'Jurnal haqida':            ('About Journal',             'О журнале'),
    "Bog'lanish":               ('Contact',                   'Контакт'),
    'Boshqaruv':                ('Management',                'Управление'),
    'Panel':                    ('Dashboard',                 'Панель'),
    'Kategoriyalar':            ('Categories',                'Категории'),
    'Maqola yozish':            ('Write Article',             'Написать статью'),
    "Yangilik qo'shish":        ('Add News',                  'Добавить новость'),
    "Jurnal qo'shish":          ('Add Journal',               'Добавить журнал'),
    "Tahririyat a'zosi qo'shish":    ('Add Editorial Member',      'Добавить члена редколлегии'),
    'J. haqidani tahrirlash':   ('Edit About Journal',        'Редактировать "О журнале"'),
    'M. yuborishni tahrirlash': ('Edit Article Submission',   'Редактировать отправку статьи'),
    'Ijtimoiy tarmoqlar':       ('Social Media',              'Социальные сети'),
    'Xabarlar':                 ('Messages',                  'Сообщения'),
    'Hisob':                    ('Account',                   'Аккаунт'),
    'Profilni tahrirlash':      ('Edit Profile',              'Редактировать профиль'),
    'Parolni almashtirish':     ('Change Password',           'Изменить пароль'),
    'Chiqish':                  ('Log out',                   'Выйти'),
    'Menyu':                    ('Menu',                      'Меню'),

    # Navbar (bottom menu)
    'Asosiy':                   ('Main',                      'Главная'),

    # Auth pages
    'Kirish':                   ('Login',                     'Войти'),
    "Ro'yxat":                  ('Register',                  'Регистрация'),
    "Ro'yxatdan o'tish":        ('Sign Up',                   'Регистрация'),
    'Ilmiy jurnal':             ('Scientific Journal',        'Научный журнал'),

    # ── Category pages ────────────────────────────────────
    'Maqola kategoriyalari':            ('Article Categories',        'Категории статей'),
    "Yangi kategoriya":                 ('New Category',              'Новая категория'),
    "Yangi kategoriya qo'shish":        ('Add New Category',          'Добавить новую категорию'),
    "Kategoriya qo'shish":              ('Add Category',              'Добавить категорию'),
    "Kategoriyalar yo'q":               ('No Categories',             'Нет категорий'),
    "Birinchi kategoriyani qo'shing":   ('Add your first category',   'Добавьте первую категорию'),
    "Hali kategoriyalar qo'shilmagan.": ('No categories added yet.',  'Категории ещё не добавлены.'),
    'Barchasi':                         ('All',                       'Все'),
    'Bekor qilish':                     ('Cancel',                    'Отмена'),
    'tahrirlash':                       ('edit',                      'редактировать'),
    "o'chirish":                        ('delete',                    'удалить'),
    "kategoriyasi o'chiriladi.":        ('category will be deleted.', 'категория будет удалена.'),
    "Haqiqatan ham o'chirmoqchimisiz?": ('Are you sure you want to delete?',   'Вы уверены, что хотите удалить?'),
    "Bu kategoriyaga biriktirilgan maqolalar kategoriyasiz qoladi.": (
        'Articles in this category will become uncategorized.',
        'Статьи в этой категории потеряют категорию.'),
    "Jami {{ count }} ta kategoriya":   ('Total {{ count }} categories',       '{{ count }} категорий всего'),

    # ── Band (section) strings ─────────────────────────────
    'Bandlar':                          ('Sections',                  'Разделы'),
    'Band nomi...':                     ('Section name...',           'Название раздела...'),
    'Band matnini yozing...':           ('Write section text...',     'Напишите текст раздела...'),
    "Hali band qo'shilmagan.":          ('No sections added yet.',    'Разделы ещё не добавлены.'),
    "Band qo'shish":                    ('Add Section',               'Добавить раздел'),
    "Yangi band qo'shish":              ('Add new section',           'Добавить новый раздел'),
    "Bu bandni o'chirmoqchimisiz?":     ('Delete this section?',      'Удалить этот раздел?'),
    'Xato!':                            ('Error!',                    'Ошибка!'),
    'Arxivda':                          ('Archived',                  'В архиве'),
    "Arxivga qo'shish":                 ('Add to archive',            'В архив'),

    # ── Journal list ───────────────────────────────────────
    'Yuklab olish':                     ('Download',                  'Скачать'),
    'Chiqarish':                        ('Remove from archive',       'Убрать из архива'),
    "Jurnallar qo'shilgandan 1 hafta o'tgach bu yerda ko'rinadi.": (
        'Journals will appear here 1 week after being added.',
        'Журналы появятся здесь через 1 неделю после добавления.'),
    '{{ total }} ta maqola':            ('{{ total }} articles',      '{{ total }} статей'),
    '{{ count }} ta maqola':            ('{{ count }} articles',      '{{ count }} статей'),

    # ── Profile / User pages ───────────────────────────────
    'Ortga':                                    ('Back',                      'Назад'),
    'Foydalanuvchi hisob qaydnomasi':           ('User Account',              'Аккаунт пользователя'),
    'Foydalanuvchi':                            ('User',                      'Пользователь'),
    "Rasm yuklash uchun quyidagi maydondan foydalaning": (
        'Use the field below to upload a photo',
        'Используйте поле ниже для загрузки фото'),
    "Shaxsiy ma'lumotlar":                      ('Personal Information',      'Личные данные'),
    'Ism':                                      ('First Name',                'Имя'),
    'Familiya':                                 ('Last Name',                 'Фамилия'),
    'Email manzil':                             ('Email Address',             'Адрес электронной почты'),
    "Qo'shimcha ma'lumotlar":                   ('Additional Information',    'Дополнительная информация'),
    'Telefon raqami':                           ('Phone Number',              'Номер телефона'),
    "Tug'ilgan sana":                           ('Date of Birth',             'Дата рождения'),

    # ── Journal list extras ────────────────────────────────
    '{{ journals|length }} ta jurnal':  ('{{ journals|length }} journals', '{{ journals|length }} журналов'),

    # ── Login page ─────────────────────────────────────────
    "Akkaunt yo'qmi?":          ("Don't have an account?",  'Нет аккаунта?'),
    "Ro'yxatdan o'ting":        ('Sign up',                 'Зарегистрироваться'),
    'Kirish':                   ('Log in',                  'Вход'),
    'Parolni tiklash':          ('Reset password',          'Восстановление пароля'),

    # ── Form field labels (Django AuthenticationForm) ──────
    'Username':                 ('Username',                'Логин'),
    'Password':                 ('Password',                'Пароль'),

    # ── Login template explicit labels ─────────────────────
    'Foydalanuvchi nomi':       ('Username',                'Логин'),
    'Parol':                    ('Password',                'Пароль'),
}

def update_po(lang_code, translation_index):
    po_path = os.path.join(BASE, 'locale', lang_code, 'LC_MESSAGES', 'django.po')
    mo_path = po_path.replace('.po', '.mo')

    if not os.path.exists(po_path):
        print(f"  {po_path} topilmadi, o'tkazildi.")
        return

    po = polib.pofile(po_path, encoding='utf-8')
    existing_ids = {e.msgid for e in po}

    added = 0
    for uz_str, translations in TRANSLATIONS.items():
        if uz_str not in existing_ids:
            entry = polib.POEntry(
                msgid=uz_str,
                msgstr=translations[translation_index],
            )
            po.append(entry)
            added += 1
        else:
            # Mavjud bo'lsa va msgstr bo'sh bo'lsa, to'ldur
            for e in po:
                if e.msgid == uz_str and not e.msgstr:
                    e.msgstr = translations[translation_index]

    po.save(po_path)
    po.save_as_mofile(mo_path)
    print(f'  {lang_code}: {added} yangi tarjima qoshildi + .mo kompilatsiya qilindi')

print('EN tarjimalari...')
update_po('en', 0)

print('RU tarjimalari...')
update_po('ru', 1)

print('Tayyor!')
