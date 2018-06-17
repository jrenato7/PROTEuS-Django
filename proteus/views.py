# coding=utf8

from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from proteus.models import Processing, Contact, Align, process_data
from proteus.forms import UploadFileForm, upload


@csrf_protect
def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            pdb_file = upload(request.FILES['pdbfile'])
            url = process_data(request.POST, pdb_file)
            return redirect('result', url=url)
    else:
        form = UploadFileForm()
    return render(request, 'index.html', {'form': form})


@csrf_protect
def result(request, url):
    try:
        process = Processing.objects.get(url=url)
        context = {
            'title': 'PDB ID: ' + process.pdbid,
            'subtitle': 'Cutoff: ' + str(process.cutoff),
            'pdbid': process.pdbid
        }
    except Processing.DoesNotExist:
        st = 'The process requested was not found in our database.'
        st += ' Please send an email to proteus.lbs@gmail.com with the '
        st += 'URL accessed!'
        context = {
            'title': 'Process not found!',
            'subtitle': 'st',
        }
    return render(request, 'result.html', context)


@csrf_protect
@require_GET
def process(request, url):
    try:
        prc = Processing.objects.get(url=url)
        ctts = Contact.objects.filter(
            id_p=prc.id_p).filter(ctt_status__gt=0).order_by('ctt_sequence')
        context = {'ps': prc.status}
        context['contacts'] = []
        mut_found = 0
        for ct in ctts:
            c = {'id': ct.id_ctt, 'title': ct.ctt_type}
            alg = Align.objects.filter(id_ctt=ct.id_ctt).order_by('al_score')
            contacts = []
            for al in alg:
                mut_found += 1
                alid = prc.url + '.' + str(ct.id_ctt) + '.' + str(al.id_alg)
                clash = "yes" if al.clash else "no"
                ddg = al.ddg
                a = {'type': al.al_type, 'pdbid': al.pdbid, 'chain': al.chain,
                     'r1': al.r1, 'r2': al.r2, 'score': al.al_score,
                     'alid': alid, 'clash': clash, 'ddg': ddg}
                contacts.append(a)
            c['contacts'] = contacts
            context['contacts'].append(c)
            context['mutation_found'] = mut_found
    except:
        context = {}
    return JsonResponse(context)