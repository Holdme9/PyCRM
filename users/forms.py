from typing import Any

from django.contrib.auth.forms import UserCreationForm, UsernameField, UserChangeForm
from django.contrib.auth import get_user_model
from django.forms import PasswordInput

User = get_user_model()


class SignupForm(UserCreationForm):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        pwd1 = self.fields['password1']
        pwd2 = self.fields['password2']
        pwd1.label = 'Пароль'
        pwd1.help_text = 'Пароль не должен быть слишком схож с другой персональной информацией.\
            <br /> Длинна пароля должна быть не менее 8 символов.\
                <br /> Пароль не должен быть слишком простым. \
                    <br /> Пароль не может состоять только из цифр.'
        pwd2.label = 'Подтвердите пароль'
        pwd2.help_text = 'Введите пароль повторно для проверки.'

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        field_classes = {'username': UsernameField}
        labels = {
            'username': 'Имя пользователя',
            'email': 'Емейл',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }


class UserUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', ]
