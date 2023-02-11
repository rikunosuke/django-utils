from django.db import models
from django.utils.functional import cached_property


class DBLog(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "サーバログ"
        get_latest_by = "id"

    created_at = models.DateTimeField(
        verbose_name="作成日時", auto_now_add=True, db_index=True
    )

    levelname = models.CharField(verbose_name="レベル", max_length=32)

    category = models.CharField(verbose_name="カテゴリ", max_length=128, blank=True)

    message = models.TextField(verbose_name="メッセージ", null=True, default=None)

    request = models.TextField(verbose_name="リクエスト", null=True, default=None)

    traceback = models.TextField(verbose_name="トレースバック", null=True, default=None)

    def __str__(self):
        return f"DbLog#{self.id}"

    @cached_property
    def pretty_message(self):
        message_list = self.message.split("\n")
        if len(message_list) > 3 and message_list[3][0] == "[":
            try:
                L = eval(message_list[3])
                message_list[3] = "".join(L)
            except SyntaxError:
                pass
        return "\n".join(message_list)
