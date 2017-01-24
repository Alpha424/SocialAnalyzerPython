from django import forms


def validate_file_extension(value):
    if not (value.name.endswith('.csv') or value.name.endswith('.xls') or value.name.endswith('.xlsx')):
        raise forms.ValidationError('Неправильный формат файла')

class FileUploadForm(forms.Form):
    file = forms.FileField(label='', validators=[validate_file_extension])

class CSVOptionsForm(forms.Form):
    SEPARATOR_CHOICES = (
        (',', 'Запятая'),
        (' ', 'Пробел'),
        (';', 'Точка с запятой'),
        ('\t', 'Горизонтальная табуляция'),
    )
    CODEC_CHOICES = (
        ('utf8', 'UTF-8'),
        ('cp1251', 'windows-1251'),
        ('ascii', 'ASCII'),
    )
    separator = forms.ChoiceField(choices=SEPARATOR_CHOICES, required=True)
    separator.widget.attrs.update({'class' : 'form-control'})
    codec = forms.ChoiceField(choices=CODEC_CHOICES, required=True)
    codec.widget.attrs.update({'class' : 'form-control'})

class XLSOptionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        sheets = kwargs.pop('sheets')
        super(XLSOptionsForm, self).__init__(*args, **kwargs)
        self.fields['sheet_selection'] = forms.ChoiceField(choices=[(idx, sheet.name) for idx, sheet in enumerate(sheets)], required=True)
        self.fields['sheet_selection'].widget.attrs.update({'class' : 'form-control'})

class EnterAttributesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        num_of_attributes = kwargs.pop('narg')
        super(EnterAttributesForm, self).__init__(*args, **kwargs)
        for i in range(num_of_attributes):
            self.fields['arg%s' % i] = forms.CharField(max_length=64, min_length=1, required=False)
            self.fields['arg%s' % i].widget.attrs.update({'class' : 'form-control'})

class ExcludeFeaturesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        attributes = kwargs.pop('attrs')
        super(ExcludeFeaturesForm, self).__init__(*args, **kwargs)
        for a in attributes:
            self.fields[a] = forms.BooleanField(label=a, required=False)


class SelectKeyAttributeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        attributes = kwargs.pop('attributes')
        super(SelectKeyAttributeForm, self).__init__(*args, **kwargs)
        self.fields['key_attribute_selection'] = forms.ChoiceField(choices=[(idx, a) for idx, a in enumerate(attributes)])
        self.fields['key_attribute_selection'].widget.attrs.update({'class' : 'form-control'})