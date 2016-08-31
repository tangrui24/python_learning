#!/usr/bin/env python
#!/usr/bin/env python

from django.forms import Form,ModelForm
from crm import models


def modelform(model_obj):
    class Modelform(ModelForm):
        class Meta:
            model = model_obj
            exclude = ()

        def __init__(self, *args, **kwargs):
            super(Modelform, self).__init__(*args, **kwargs)
            for field_name in self.base_fields:
                field = self.base_fields[field_name]
                field.widget.attrs.update({'class': 'form-control'})
    return Modelform