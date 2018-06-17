# -*- coding: UTF-8 -*-
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

from math import sqrt

import hashlib
import datetime
import copy


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
    status = models.IntegerField(default=0)
    pdbid = models.CharField(max_length=45)
    cutoff = models.FloatField(default=0.5)
    url = models.CharField(max_length=64)
    notification_user = models.IntegerField(blank=True, null=True, default=0)

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
    ctt_status = models.IntegerField(default=0)
    ctt_chain = models.CharField(max_length=4)
    ctt_sequence = models.IntegerField(default=100000)
    ctt_clash = models.IntegerField(default=0)
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
    sequence = models.IntegerField(default=1000000)
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


RESIDUEDICT = {'ALA': 'A', 'ARG': 'R', 'ASP': 'D', 'ASN': 'N', 'CYS': 'C',
               'GLU': 'E', 'GLN': 'Q', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
               'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
               'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'}

RESIDUEDICT2 = {'A': 'ALA', 'R': 'ARG', 'D': 'ASP', 'N': 'ASN', 'C': 'CYS',
                'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS', 'I': 'ILE',
                'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO',
                'S': 'SER', 'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL'}

MAINCHAIN = ["N", "CA", "C", "O"]


def process_data(data, pdb_file):
    user, created = User.objects.get_or_create(
        email=data['email'] )
    if created:
        user.name = data['name']
        user.save()
    user_id = user.id_u
    cutoff = data['cutoff']
    pdb_name = pdb_file.split('/')[-1].split('.')[0]
    url = ''.join([pdb_name, cutoff, str(user_id)])
    url = generate_url(url)
    prc = Processing.objects.create(
        id_user=user, pdbid=pdb_name, cutoff=cutoff, url=url, status=0)

    if not data.get('all_residues'):
        residue = get_residue_info(data['residue'])
        #  definimos o raio padrão para 10A.
        ray = 10
        residues_in_ray = cut_pdb(pdb_file, residue[0], residue[1],
                                  data.get('chain'), ray)
    else:
        residues_in_ray = []
    gc = GenerateContactsPdbFile(pdb_file, chain=data.get('chain'),
                                 residues_in_ray=residues_in_ray)
    #for m in gc.messages:
    #    flash(m)
    store_contacts(gc, prc)
    """send_mail_process_start(mail, user.email, user.name, prc.url,
                            prc.pdbid, prc.cutoff, request.url)"""
    return prc.url


def store_contacts(gc, id_p):
    lst_ctt_prot = prepare_res_align(gc)
    for ctt in gc.contacts:
        rn1_ct = gc.residues[ctt[0]][0]
        rn2_ct = gc.residues[ctt[1]][0]
        ct_name = RESIDUEDICT[rn1_ct] + str(ctt[0]) + '-'
        ct_name += RESIDUEDICT[rn2_ct] + str(ctt[1])
        c = Contact.objects.create(
            id_p=id_p, ctt_type=ct_name, ctt_status=0,
            ctt_chain=str(gc.chain.id), ctt_sequence=ctt[0])
        f1 = []  # receive the contacts from pdb uploaded
        #     first triple           second triple
        lp = lst_ctt_prot[ctt[0]] + lst_ctt_prot[ctt[1]]
        for c1 in lp:
            f1 += copy.deepcopy(c1)
        for i, f in enumerate(f1):
            tpa = 1 if f['name'] in MAINCHAIN else 0
            a = Atom.objects.create(
            id_ctt=c, sequence=i, name=f['name'], level=f['level'],
            bfactor=f['bfactor'], occupancy=f['occupancy'], element=f['element'],
            serial_number=f['serial_number'], fullname=f['fullname'],
            coord=f['coord'], type=tpa)


def generate_url(url):
    dt = str(datetime.datetime.now())
    url += dt
    e = hashlib.sha256()
    e.update(url.encode())
    return e.hexdigest()


def get_residue_info(res):
    i = -1
    while res[i].isdigit():
        i -= 1
    res_name = res[:i + 1] if len(res[:i + 1]) == 3 else RESIDUEDICT2[res[:i + 1]]
    res_pos = res[i + 1:]
    return [res_name, res_pos]


def cut_pdb(pdb_file, res_name, res_position, chain='A', ray=10):
    atoms = []
    residues = []
    main_resid_coords = []
    with open(pdb_file) as pdbf:
        for ln in pdbf.readlines():
            if ln[0:4] == 'ATOM' and ln[21] == chain:
                atoms.append([ln[17:20], ln[22:26].strip(), float(ln[30:38]),
                float(ln[38:46]), float(ln[46:54]), ln])
                # get the main_resid_coordsinates of main resdue
                if res_name == ln[17:20] and res_position == ln[22:26].strip():
                    main_resid_coords.append([
                        float(ln[30:38]),
                        float(ln[38:46]),
                        float(ln[46:54])])
    pdbf.close()
    for c in main_resid_coords:
        x, y, z = c
        for atom in atoms:
            # euclidian distance
            ed = sqrt((x - atom[2])**2 + (y - atom[3])**2 + (z - atom[4])**2)
            if ed < ray and atom[1] not in residues:
                residues.append(atom[1])

    pdb_cutted = pdb_file.replace('.pdb', '') + '_cutted.pdb'
    save = open(pdb_cutted,'w')
    for atom in atoms:
        if atom[1] in residues:
            save.write(atom[5])

    save.write('TER\nEND')
    save.close()
    return residues


def prepare_res_align(gc):
    """
    type (GenerateContactsPdbFile) -> dict
    :param gc: object of GenerateContactsPdbFile class.
    :return:dict key = residue_id; value = list atoms of triple.
    [[Atom N, Atom CA, Atom C, Atom O], [Atom N,
    Atom CA, Atom C, Atom O], [Atom N, Atom CA, Atom C,
    Atom O]]
    """
    dict_ret = {}
    for ctc in gc.contacts:
        if ctc[0] not in dict_ret:
            ret = prepare_res_align_aux(ctc[0], gc)
            if len(ret) > 0:
                dict_ret[ctc[0]] = ret[:]
        if ctc[1] not in dict_ret:
            ret2 = prepare_res_align_aux(ctc[1], gc)
            if len(ret2) > 0:
                dict_ret[ctc[1]] = ret2[:]
    return dict_ret


def prepare_res_align_aux(r, gc):
    # type (int, GenerateContactsPdbFile) -> list
    full_n = gc.get_neighborhood_residue(r)
    lst = []
    for fn in full_n:
        if fn == r:
            lst.append(gc.residues[fn][1])
        else:
            tmp = []
            for rngb in gc.residues[fn][1]:
                if rngb['name'] in MAINCHAIN:
                    tmp.append(rngb)
            lst.append(tmp)
    return lst