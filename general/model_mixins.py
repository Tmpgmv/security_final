from django.urls import reverse_lazy


class TypicalUrlMixin:
    def get_absolute_url(self):
        return reverse_lazy(f"{self._meta.model_name}_detail", kwargs={"pk": self.pk})

    def get_delete_url(self):
        return reverse_lazy(f"{self._meta.model_name}_delete", kwargs={"pk": self.pk})

    def get_update_url(self):
        return reverse_lazy(f"{self._meta.model_name}_update", kwargs={"pk": self.pk})


