# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `` lines if you wish to allow Django to create, modify, and delete
# the table
# Feel free to rename the models, but don't rename db_table values or field
# names.

from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from .generate_contacts import GenerateContactsPdbFile


class User(models.Model):
    id_u = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    email = models.CharField(unique=True, max_length=150)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.name

class Processing(models.Model):
    id_p = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(
        User, related_name='user',on_delete=models.CASCADE)  # type: User
    status = models.IntegerField()
    pdbid = models.CharField(max_length=45)
    cutoff = models.FloatField()
    url = models.CharField(max_length=64)
    notification_user = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'processing'

    def __str__(self):
        return self.pdbid + " " + self.id_user.name

    def get_absolute_url(self):
        return reverse('result', kwargs={'url': self.url})


class Contact(models.Model):
    id_ctt = models.AutoField(primary_key=True)
    id_p = models.ForeignKey(
        Processing, related_name='process', on_delete=models.CASCADE)
    ctt_type = models.CharField(max_length=30)
    ctt_status = models.IntegerField()
    ctt_chain = models.CharField(max_length=4)
    ctt_sequence = models.IntegerField()
    ctt_clash = models.IntegerField()
    ctt_ddg = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        db_table = 'contact'

    def __str__(self):
        return str(self.id_ctt) + " " +  self.ctt_type


class Align(models.Model):
    id_alg = models.AutoField(primary_key=True)
    id_ctt = models.ForeignKey(Contact, on_delete=models.CASCADE)
    id_ctt_search_db = models.IntegerField()
    al_score = models.FloatField()
    al_type = models.CharField(max_length=7)
    chain = models.CharField(max_length=1)
    pdbid = models.CharField(max_length=5)
    r1 = models.CharField(max_length=7)
    r2 = models.CharField(max_length=7)
    rotation = models.TextField()
    translation = models.TextField()
    clash = models.IntegerField()
    ddg = models.FloatField(blank=True, null=True, default=None)

    class Meta:
        db_table = 'align'


class Atom(models.Model):
    id_atom = models.AutoField(primary_key=True)
    id_ctt = models.ForeignKey(Contact, on_delete=models.CASCADE)
    sequence = models.IntegerField()
    name = models.CharField(max_length=5)
    level = models.CharField(max_length=5)
    bfactor = models.FloatField()
    occupancy = models.FloatField()
    element = models.CharField(max_length=10)
    serial_number = models.IntegerField()
    fullname = models.CharField(max_length=10)
    coord = models.CharField(max_length=30)
    type = models.IntegerField()

    class Meta:
        db_table = 'atom'


class AtomAlign(models.Model):
    id_atom = models.AutoField(primary_key=True)
    name = models.CharField(max_length=5)
    level = models.CharField(max_length=5)
    bfactor = models.FloatField()
    occupancy = models.FloatField()
    element = models.CharField(max_length=10)
    serial_number = models.IntegerField()
    fullname = models.CharField(max_length=10)
    coord = models.CharField(max_length=25)
    id_align = models.ForeignKey(
        Align, related_name='align', on_delete=models.CASCADE)

    class Meta:
        db_table = 'atom_align'


def validated_data(data):
    # file = data.files['pdbfile']
    user = get_user(form.name.data, form.email.data)
    user_id = user.id_u
    filename = secure_filename(file.filename)
    fs = os.path.join(up_f, filename)
    file.save(fs)
    cutoff = form.cutoff.data
    pdb_name = filename.split('.')[0]
    url = generate_url(pdb_name + str(cutoff) + str(user_id))
    prc = Processing(user_id, pdb_name, cutoff, url)
    db_session.add(prc)
    db_session.commit()
    if not form.all_residues:
        residue = get_residue_info(form.residue.data)
        #  definimos o raio padrão para 10A.
        ray = 10
        residues_in_ray = cut_pdb(fs, residue[0], residue[1],
                                  form.chain.data, ray)
    else:
        residues_in_ray = []
    gc = GenerateContactsPdbFile(fs, chain=form.chain.data,
                                 residues_in_ray=residues_in_ray)
    for m in gc.messages:
        flash(m)
    store_contacts(gc, prc.id_p)
    send_mail_process_start(mail, user.email, user.name, prc.url,
                            prc.pdbid, prc.cutoff, request.url)