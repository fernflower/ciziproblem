# -*- coding: utf-8 -*-
"""
This single file takes care of generating each and every form at https://ciziproblem.cz
"""

import datetime
import json
import os
import tempfile
import yaml

import jinja2

from bottle import (BaseRequest, default_app, get, post, request, redirect, route, run, static_file)

import exc
import generate as gen

BaseRequest.MEMFILE_MAX = 1024 * 1024 * 10

DATA_DIR = "./data"
TOKEN_GET = os.getenv('TOKEN_GET')
TOKEN_POST = os.getenv('TOKEN_POST')
TOKEN_MISMATCH_REDIRECT_URL = 'https://www.petice.com/petice_za_vstup_dti_vech_pracujicich_v_r_do_systemu_zdravotniho_pojitni'
EXAMS_DATAFILE_ROOT = 'data/files/trvalypobytexamchecker'
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'


def get_form_context(filename):
    """Returns a list of form fields and a dict of system fields - a form context dict and a system context dict"""
    system_context = {}
    with open(os.path.join(DATA_DIR, 'contexts', filename), encoding='utf-8') as f:
        if filename.endswith('.yaml'):
            # context is a yaml file
            context = yaml.safe_load(f)
            document = context.get('document', {})
            try:
                # transform system keys to __key__
                document = context['document']
                for key in [k for k in document if k != "form"]:
                    # flatten dict in case of declinations - pass a dict of declinationPAD
                    if key == "declination":
                        for pad, values in document["declination"].items():
                            declination_key = "declination{}".format(pad)
                            system_context[declination_key] = {v["before"]: v["after"] for v in values}
                    elif key.endswith("_map"):
                        # that is a mapping to be used in the templates. Substitute yaml dict keys with the value of
                        # the 'name' parameter of each item while keeping the values as is
                        system_context[key] = {v['name']: v for k, v in document[key].items()}
                    else:
                        system_context['__{}__'.format(key)] = document[key]
                # process form fields
                form_fields = document['form'].get('fields', [])
            except KeyError as err:
                raise exc.ConfigError("{} raised when processing {}".format(err, filename))
        else:
            raise NotImplementedError("Only yaml contexts are supported")
        return form_fields, system_context


def get_offices_list():
    with open(os.path.join(DATA_DIR, 'minvnitra_offices'), encoding='utf8') as f:
        offices = yaml.safe_load(f)
    return offices['offices']


OFFICES = get_offices_list()
TEMPLATE_MAP = {
        "Žádost o přidělení rodného čísla": {
            "template": "zadost_rodne_cislo.docx",
            "context": "rodne_cislo_context.yaml"},
        "Historie pobytu": {
            "template": "zadost_o_historie_pobytu.docx",
            "context": "historie_pobytu_context.yaml"},
        "Potvrzení o současném pobytu": {
            "template": "zadost_potvrzeni_soucasneho_pobytu.docx",
            "context": "potvrzeni_o_soucasnem_pobytu_context.yaml"},
        "Žádost o uplatnění opatření proti nečinnosti": {
            "template": "zadost_o_uplatneni_opatreni_proti_necinnosti_spravniho_organu_Nin1.docx",
            "context": "necinnost_Nin1_context.yaml"
            },
        "Žádost o urychlení řízení": {
            "template": "zadost_urychleni_rizeni.docx",
            "context": "urychleni_rizeni_context.yaml"
            },
        "Cestování mimo okres: prohlášení": {
            "template": "COVID19-okresy_formular_cesta_mimo_okres.docx",
            "context": "covid19_okresy_prohlaseni.yaml"
            },
        "Žádost o vydání potvrzení o daňovém domicilu": {
            "template": "zadost_domicil.docx",
            "context": "domicil_context.yaml"
            },
        "Upozornění na splnění podmínek pro přiznání dávek státní sociální podpory": {
            "template": "upozorneni_na_splneni_podminek_ssp.docx",
            "context": "rodicovsky_prispevek_context.yaml"
            },
        "Čestné prohlášení o nepobírání dávek v jiném státě": {
            "template": "cestne_prohlaseni_o_nepobirani_davek.docx",
            "context": "cestne_prohlaseni_o_nepobirani_davek_context.yaml"},
        "Prohlášení o dlouhodobém pobytu v cizině (UA)": {
            "template": "prohlaseni_pobyt_v_cizine_ua.docx",
            "context": "prohlaseni_pobyt_v_cizine_ua.yaml"
            },
        "Stížnost na nedostupnost zdravotní péče": {
            "template": "stiznost_pvzp.docx",
            "context": "stiznost_pvzp_context.yaml"
            },
        }
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./views'),
    extensions=['jinja2.ext.i18n']
)


def _prepare_for_front(form_fields):
    #j2 template expects a straightforward structure of { elemname: {'value': .., 'input': ..} }
    context_to_pass = {}
    allowed_types = ["radio", "date", "checkbox", "text"]
    for field in form_fields:
        # check if specific type of input is required, if no given it will be text
        elem = {'value': field.get("default", ""), 'input': "text"}
        if field.get('conditional'):
            elem['conditional'] = field.get('conditional')
        if field.get("type", "text") != "text":
            if field["type"] in allowed_types:
                elem["input"] = field["type"]
            if field["type"] == "radio":
                elem["ids"] = field["choices"]
        context_to_pass[field["name"]] = elem
    return context_to_pass


def docform(form_fields, system_context):
    template = env.get_or_select_template('docform.tpl')
    context_to_pass = _prepare_for_front(form_fields)
    return template.render(context=context_to_pass,
                           system_context=system_context,
                           minvnitra_offices=get_offices_list())


def _timestamp_to_str(timestamp, dt_format=DATETIME_FORMAT):
    """Convert timestamp to a human-readable format"""
    try:
        int_timestamp = int(float(timestamp))
        return datetime.datetime.fromtimestamp(int_timestamp).strftime(dt_format)
    except (ValueError, TypeError):
        return ''


@get('/trvaly-pobyt/a2/lastupdate')
def get_last_update(update_time_file='lastupdate'):
    # Let's make this method not require a token for visibility purposes
    if request.query.readable:
        with open(os.path.join(EXAMS_DATAFILE_ROOT, update_time_file)) as f:
            ts = f.read()
        try:
            last_update_ts = int(float(ts))
        except (ValueError, TypeError):
            last_update_ts = 0
        last_update = _timestamp_to_str(ts)
        delta = int(datetime.datetime.now().timestamp() - last_update_ts)
        return f'Last update happened at {last_update}, <b>{delta}</b> seconds ago.'
    # return just the file itself
    return static_file(update_time_file, root='data/files/trvalypobytexamchecker/')


@get('/trvaly-pobyt/a2/<filepath>')
def get_exams_info(filepath):
    token = request.query.token
    if not token or token != TOKEN_GET:
        # token mismatch, show petition page instead
        return redirect(TOKEN_MISMATCH_REDIRECT_URL)
    # if token is ok -> show stored data
    return static_file(filepath, root='data/files/trvalypobytexamchecker/')


@post('/trvaly-pobyt/a2/<filepath>')
def post_exams_info(filepath, update_time_file='lastupdate'):
    token = request.forms.token
    if not token or token != TOKEN_POST:
        # token mismatch, show petition page instead
        return redirect(TOKEN_MISMATCH_REDIRECT_URL)
    # if token is ok -> update data and show stored data
    with open(os.path.join(EXAMS_DATAFILE_ROOT, filepath), 'w') as f:
        f.write(request.forms.html)
    # set last update date
    with open(os.path.join(EXAMS_DATAFILE_ROOT, update_time_file), 'w') as f:
        f.write(request.forms.date)
    return static_file(filepath, root=EXAMS_DATAFILE_ROOT)


@route('/')
def index():
    template = env.get_or_select_template('index.tpl')
    with open(os.path.join(DATA_DIR, 'documents')) as f:
        documents = yaml.safe_load(f)
    doc_groups = sorted({doc.get('group', 'default') for doc in documents.get('documents', [])})
    documents_per_group = [[d for d in documents.get('documents', []) if d.get('group', 'default') == group]
                           for group in doc_groups]
    return template.render(documents=documents_per_group)


@route('/necinnost_Nin1')
def necinnost():
    return docform(*get_form_context('necinnost_Nin1_context.yaml'))


@route('/rodne_cislo_application')
def rodne_cislo():
    return docform(*get_form_context('rodne_cislo_context.yaml'))


@route('/historie_pobytu')
def historie_pobytu():
    return docform(*get_form_context('historie_pobytu_context.yaml'))


@route('/potvrzeni_o_soucasnem_pobytu')
def potvrzeni_soucasny_pobyt():
    return docform(*get_form_context('potvrzeni_o_soucasnem_pobytu_context.yaml'))


@route('/urychleni_rizeni')
def urychleni_rizeni():
    return docform(*get_form_context('urychleni_rizeni_context.yaml'))


@route('/covid19_cestovani_mimo_okres')
def covid19_prohlaseni():
    return docform(*get_form_context('covid19_okresy_prohlaseni.yaml'))


@route('/danovy_domicil')
def danovy_domicil():
    return docform(*get_form_context('domicil_context.yaml'))


@route('/rodicovsky_prispevek')
def rodicovsky_prispevek():
    return docform(*get_form_context('rodicovsky_prispevek_context.yaml'))


@route('/rodicovsky_prispevek_cestne_prohlaseni')
def rodicovsky_prispevek_affidavit():
    return docform(*get_form_context('cestne_prohlaseni_o_nepobirani_davek_context.yaml'))


@route('/prohlaseni_pobyt_v_cizine_ua')
def prohlaseni_pobyt_v_cizine_ua():
    return docform(*get_form_context('prohlaseni_pobyt_v_cizine_ua.yaml'))


@route('/stiznost_pvzp')
def stiznost_pvzp():
    return docform(*get_form_context('stiznost_pvzp_context.yaml'))


def get_office_by_name(name):
    return next((o for o in OFFICES if o['name'] == name), None)


@route('/get_office_address', method="POST")
def get_office_address():
    data = request.forms
    office = get_office_by_name(data.get('office'))
    return json.dumps(office or {})


@route(r'/static/files/<filepath:re:.*\.(pdf|xml)>')
def files(filepath):
    return static_file(filepath, root='data/files')


def _apply_post_processing_hacks(context, form_fields):
    "Hacks to convert data received from frontend to the expected form in docx templates"
    # transition from YYYY-MM-DD dates to expected DD.MM.YYYY
    for date_key in [f["name"] for f in form_fields if f.get("type") == "date"]:
        try:
            context[date_key] = datetime.datetime.strptime(context[date_key], '%Y-%M-%d').strftime('%d.%M.%Y')
        except (TypeError, ValueError):
            # if anything breaks - just have it as is
            pass
    # process chosen office: substitute name with full information
    if '__chosen_office' in context:
        context['chosen_office'] = get_office_by_name(context.get('__chosen_office')) or \
                                   get_office_by_name('Pracoviště Praha V.')
    # add _checkbox to active checkbox fields
    for checkbox in [f for f in form_fields if f.get("type") == "checkbox"]:
        context['{}_checkbox'.format(checkbox['name'])] = 'True' if context[checkbox['name']] else 'False'


@route('/generate', method="POST")
def generate():
    data = request.forms
    form_name = data.get('__form__')
    docx_template_name = TEMPLATE_MAP.get(form_name, {}).get('template')
    context_name = TEMPLATE_MAP.get(form_name, {}).get('context')
    if not docx_template_name or not context_name:
        raise exc.ConfigError("No routing specified for {}".format(form_name))
    form_fields, system_context = get_form_context(context_name)
    # vet against default context keys
    allowed_keys = [f["name"] for f in form_fields] + ['__chosen_office']
    user_input_vetted = {k: v for k, v in data.iteritems() if k in allowed_keys and v}
    context = {f["name"]: f.get("default", "") for f in form_fields}
    context.update(system_context)
    context.update(user_input_vetted)
    _apply_post_processing_hacks(context, form_fields)
    with tempfile.NamedTemporaryFile(dir="generated", delete=True) as temp_doc:
        docx_template_name = os.path.join(DATA_DIR, "application_templates", docx_template_name)
        gen.generate_doc(docx_template_name, context, temp_doc.name)
        return static_file(temp_doc.name.rsplit(os.path.sep)[-1],
                           root="generated/",
                           mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           download=docx_template_name)

app = default_app()

if __name__ == '__main__':
    run(app, host='127.0.0.1', port=8080)
