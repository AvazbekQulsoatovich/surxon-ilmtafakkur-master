from django import forms
from .models import Profile, User


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-control my-2'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control my-2',
        'placeholder': 'Password confirm'}))

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'
        )
        model = User

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'example@gmail.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'Last name'
            })
        }

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")
        if password2 != self.cleaned_data["password"]:
            raise forms.ValidationError("Password not match!")

        return password2

    def clean_email(self):

        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bunday e-mailli faydalanuvchi mavjud!")

        return email


class ProfileCreateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'telephone',
            'photo',
            'date_birth',
        )
        widgets = {
            'telephone': forms.TextInput(attrs={
                'class': 'form-control my-2',
                'placeholder': '+998998765432'
            }),

            'photo': forms.FileInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'Photo for profile'
            }),
            'date_birth': forms.DateInput(attrs={
                'class': 'form-control my-2', 'placeholder': "yil-oy-kun | 2000-01-01",
                'type': 'date'
            }),
        }

    def clean_telephone(self):

        telephone = self.cleaned_data['telephone']
        if telephone:
            if len(telephone) == 13 and telephone.startswith("+998"):
                numbers: str = telephone[3:]
                if numbers.isdigit():
                    return telephone
            else:
                raise forms.ValidationError('Invalid telephone number')
        return telephone


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'example@gmail.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control my-2',
                'placeholder': 'Last name'
            })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Bunday e-mailli faydalanuvchi mavjud!")

        return email


