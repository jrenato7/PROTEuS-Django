#
import re

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
import os
import magic

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "")

ALLOWED_EXTENSIONS = ('pdb')
ALLOWED_MIMES = ('text/plain', 'chemical/x-pdb')


class UploadFileForm(forms.Form):
    name = forms.CharField(label='Name', max_length=128, required=True)
    email = forms.EmailField(label='Email Address')
    chain = forms.CharField(label='Chain', max_length=2)
    # , render_kw={'placeholder': 'A', 'class': '', 'value': 'A'}
    """pdbfile = FileField(
    'PDB File', [validators.Regexp(u'([0-9A-Za-z0-9])*\.pdb$')])"""
    """cutoff = forms.FloatField('Cutoff', [validators.NumberRange(
            min=0.0, max=2.0)], render_kw={'placeholder': '0.5', 'class': 
            ''})"""
    residue = forms.CharField(label='Residue', min_length=2)
    pdbfile = forms.FileField(label='PDB File', required=True)
    all_residues = forms.BooleanField(label='All Residues', required=False)

    def clean_pdbfile(self):
        pdbfile = self.cleaned_data['pdbfile']
        mime = magic.from_buffer(pdbfile.read(), mime=True)
        if mime not in ALLOWED_MIMES:
            raise ValidationError(
                "The uploaded file is not a valid PDB file.")

        for chuck in pdbfile.chunks():
            if 'ATOM' in str(chuck):
                return pdbfile
        raise ValidationError(
            "The uploaded file is not in the valid PDB format.")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload(pdb_f):
    with open(os.path.join(settings.MEDIA_ROOT, pdb_f.name),
              'wb+') as destination:
        for chunk in pdb_f.chunks():
            destination.write(chunk)


def verify_pdbfile(files):
    if 'pdbfile' not in files:
        msg = 'Please, choose a PDB file!'
    else:
        file = files['pdbfile']
        r = re.compile(u'([0-9A-Za-z0-9])*\.pdb$')
        if r.match(file.filename.lower()):
            msg = None
        else:
            msg = 'Invalid input. It should be in "*.pdb" format'
    return msg
