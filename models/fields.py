from base64 import b64encode, b64decode
from django.conf import settings
from django.db import models

from django_utils.encryption import encrypt, decrypt


class EncryptedFieldMixin:
    """
    Djangoのモデルフィールドを、DB登録時に暗号化するように
    変更するMixin
    戻り値が str のため、models.BinaryFieldなどには使えない
    """

    def pre_save(self, model_instance, add):
        """
        model_instanceがもつフィールドの値を暗号化する。
        """
        value = getattr(model_instance, self.attname)
        return b64encode(encrypt(value, settings.ENCRYPTION_KEY)).decode(
            'utf-8')

    def from_db_value(self, cipher_with_iv, expression, connection):
        """
        DBから取り出したフィールドの値を復号化する。
        暗号化されていないデータが混在しているため、
        一時的にtryでエラー処理をしている。
        """
        try:
            cipher_with_iv_binary = b64decode(cipher_with_iv)
            return decrypt(cipher_with_iv_binary, settings.ENCRYPTION_KEY)
        except ValueError:
            return cipher_with_iv


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    """
    データをDB登録時に自動で暗号化するフィールド
    TextFieldを継承しているため、ModelAdminやModelFormでも
    TextFieldと同じように使える。
    マイグレーションファイルは生成されるが DBのデータ型は同じため、
    既存のTextFieldとの置き換えが可能。
    """
    pass


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    pass
