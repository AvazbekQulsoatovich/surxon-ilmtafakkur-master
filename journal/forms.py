import os
from django import forms

from .models import Contact, Article, Post, Journal, SocialMedia, About, SendingArticle, Editorial, Category, SitePage, Submission, YearCategory


class SitePageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        textarea_attrs = {
            'class': 'form-control mb-4 mt-1',
            'rows': 10,
        }
        placeholders = {
            'content': 'Kontent (Asosiy)',
            'content_uz': "Kontent (O'zbek)",
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget = forms.Textarea(attrs={
                **textarea_attrs,
                'placeholder': placeholder,
            })

    class Meta:
        model = SitePage
        fields = ('content', 'content_uz')
        labels = {
            'content': "Kontent (Asosiy)",
            'content_uz': "Kontent (O'zbek)",
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('message',)

        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control my-4 border-1 w-100', 'placeholder': 'Message',
            }),
        }

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError("Xabar bo'sh bo'lmasligi kerak!")
        return message


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'color')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Kategoriya nomi'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control', 'type': 'color'
            }),
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx']
    MAX_SIZE_MB = 20

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True, 'class': 'mb-4 mt-1 form-control'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        import os
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        result = [f for f in result if f]
        if not result and self.required:
            raise forms.ValidationError(self.error_messages['required'], code='required')
        # Validate each file
        for f in result:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f"Faqat {', '.join(self.ALLOWED_EXTENSIONS)} formatdagi fayllar ruxsat etiladi."
                )
            if f.size > self.MAX_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f"Fayl hajmi {self.MAX_SIZE_MB}MB dan oshmasligi kerak."
                )
        return result

class ArticleForm(forms.ModelForm):
    additional_pdfs = MultipleFileField(
        required=False,
        label="Qo'shimcha fayllar (PDF, DOC, DOCX - bir nechta tanlash mumkin)"
    )

    class Meta:
        model = Article
        fields = (
        'title', 'title_uz', 'authors', 'journal', 'published_date', 'doi', 'pages', 'abstract', 'keywords', 'references', 'content', 'content_uz', 'pdf_file', 'additional_pdfs')

        labels = {
            'title': 'Maqola sarlavhasi (asosiy)',
            'title_uz': "Maqola sarlavhasi (o'zbek tilida, ixtiyoriy)",
            'authors': 'Mualliflar',
            'journal': 'Jurnal soni (qaysi songa tegishli)',
            'published_date': 'Nashr qilingan sana (ixtiyoriy)',
            'doi': 'DOI raqami yoki havolasi',
            'pages': 'Sahifalar',
            'abstract': 'Annotatsiya (Abstract)',
            'keywords': "Kalit so'zlar",
            'references': 'Foydalanilgan adabiyotlar',
            'content': 'Maqola matni (ixtiyoriy, PDF bo\'lsa kerak emas)',
            'content_uz': "Maqola matni (o'zbek tilida, ixtiyoriy)",
            'pdf_file': 'Asosiy PDF fayl',
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Masalan: Surxondaryo viloyatida...',
            }),
            'title_uz': forms.TextInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Maqola sarlavhasi o\'zbek tilida (ixtiyoriy)',
            }),
            'journal': forms.Select(attrs={
                'class': 'mb-4 mt-1 form-control',
            }),
            'published_date': forms.DateInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'type': 'date'
            }),
            'doi': forms.TextInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Masalan: https://doi.org/10.37547/surxon-2024-1-15',
            }),
            'pages': forms.TextInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Masalan: 84–91 (bosh sahifa va oxirgi sahifa)',
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': "Kalit so'zlarni vergul bilan ajrating: tarix, arxiv, Surxondaryo",
            }),
            'authors': forms.TextInput(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Masalan: Karimov Jasur Olimovich, Toshmatov Sardor',
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'mb-4 mt-1 form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Translation fields and other optional fields should not block form validation
        for field in ['title_uz', 'content_uz', 'authors']:
            if field in self.fields:
                self.fields[field].required = False
        # Journal select uchun bo'sh tanlov
        self.fields['journal'].empty_label = '--- Jurnal sonini tanlang ---'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
        'title', 'title_uz', 'content', 'content_uz', 'mediaImage')

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sarlavha'
            }),
            'title_uz': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sarlavha_uz'
            }),
            'mediaImage': forms.FileInput(attrs={
                'class': 'form-control', 'placeholder': 'Rasm yoki Video yuklang'
            }),
            'content': forms.Textarea(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Content'
            }),
            'content_uz': forms.Textarea(attrs={
                'class': 'mb-4 mt-1 form-control',
                'placeholder': 'Content_uz'
            }),
        }


class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ('image', 'file', 'year_category', 'source_number')

        labels = {
            'image': 'Jurnal muqovasi (rasm)',
            'file': 'Jurnal to\'liq PDF fayli',
            'year_category': 'Jurnal yili (avval yil yarating)',
            'source_number': 'Jurnal soni (masalan: 1, 2, 3...)',
        }

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jurnal muqova rasmini yuklang (PNG, JPG)'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jurnal to\'liq PDF faylini yuklang'
            }),
            'year_category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'source_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jurnal sonini kiriting (masalan: 1, 2, 3)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(JournalForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['file'].required = False
        self.fields['year_category'].empty_label = '--- Yilni tanlang ---'

class YearCategoryForm(forms.ModelForm):
    class Meta:
        model = YearCategory
        fields = ('year', 'is_active')
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Yilni kiriting (masalan, 2024)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class SocialForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        fields = ('title', 'url', 'color')

        widgets = {
            'title': forms.Select(attrs={
                'class': 'form-control'
            }),
            "url": forms.URLInput(attrs={
                'class': 'form-control'
            }),
            'color': forms.Select(attrs={
                'class': 'form-control'
            })
        }


class SendingArticleForm(forms.ModelForm):
    class Meta:
        model = SendingArticle
        fields = ('content', 'content_uz')

        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control my-4 border-1 w-100', 'placeholder': 'Content',
            }),
            'content_uz': forms.Textarea(attrs={
                'class': 'form-control my-4 border-1 w-100', 'placeholder': 'Content_uz',
            }),
        }


class EditorialForm(forms.ModelForm):
    class Meta:
        model = Editorial
        fields = ('image', 'first_name', 'last_name', 'phone_number', 'position', 'description')

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control', 'placeholder': 'Jpg, Png'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control my-2', 'placeholder': 'Ism'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control my-2', 'placeholder': 'Familiya'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control my-2', 'placeholder': '+998901234567 (ixtiyoriy)'
            }),
            'position': forms.Select(attrs={
                'class': 'form-select my-2',
            }, choices=[
                ('bosh_muharrir', "Bosh muharrir"),
                ('tahrir_azosi', "Tahrir hay'ati a'zosi"),
            ]),
            'description': forms.Textarea(attrs={
                'class': 'form-control my-2',
                'placeholder': "Masalan: Fizika-matematika fanlari doktori, professor, O'zbekiston FA akademigi",
                'rows': 3,
            }),
        }


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = (
        'journal_name', 'journal_name_uz', 'content', 'content_uz',
        'journal_image',
        'author_description', 'author_description_uz', 'author_image')

        widgets = {
            'journal_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sarlavha',
            }),
            'journal_name_uz': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sarlavha_uz',
            }),
            'content': forms.Textarea(attrs={
                'class': 'mb-4 mt-1 form-control', 'placeholder': 'Content',
            }),
            'content_uz': forms.Textarea(attrs={
                'class': 'mb-4 mt-1 form-control', 'placeholder': 'Content_uz',
            }),
            'journal_image': forms.FileInput(attrs={
                'class': 'form-control', 'placeholder': 'Rasm',
            }),
            'author_description': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Muallif haqida...',
            }),
            'author_description_uz': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Muallif haqida_uz...',
            }),
            'author_image': forms.FileInput(attrs={
                'class': 'form-control', 'placeholder': 'Rasm',
            })
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('title', 'abstract', 'file')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': "Maqola sarlavhasi (uz, ru yoki en)",
                'required': 'true'
            }),
            'abstract': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'placeholder': "Maqola annotatsiyasi / qisqacha mazmuni...",
                'rows': 5,
                'required': 'true'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control mb-3',
                'required': 'true'
            })
        }


class SubmissionReviewForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('status', 'feedback')
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select mb-3'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'placeholder': "Tahririyat taqrizi va muallifga izohlar...",
                'rows': 4
            })
        }

