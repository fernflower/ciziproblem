import datetime
import jinja2
import json
import os
import tempfile
import yaml

from bottle import default_app, request, route, run, static_file

import generate as gen


def _default_context(filename):
    """Returns a default context dict"""
    with open(filename) as f:
        try:
            data = json.loads(f.read())
            if data['__postal_address__'] == 'minvnitra_offices_chooser':
                data['__chosen_office'] = None
            return data
        except:
            return {}

def get_offices_list():
    with open('minvnitra_offices', encoding='utf8') as f:
        offices = yaml.safe_load(f)
    return offices['offices']


OFFICES = get_offices_list()
TEMPLATE_MAP = {
        "Trvalý pobyt: Žádost o uplatnění opatření proti nečinnosti": {
            "template": "zadost_o_uplatneni_opatreni_proti_necinnosti_spravniho_organu.docx",
            "context": "necinnost_trvaly_context"},
        "Žádost o přidělení rodného čísla": {
            "template": "zadost_rodne_cislo.docx",
            "context": "rodne_cislo_context"},
        "Historie pobytu": {
            "template": "zadost_o_historie_pobytu.docx",
            "context": "historie_pobytu_context"},
        "Potvrzení o současném pobytu": {
            "template": "zadost_potvrzeni_soucasneho_pobytu.docx",
            "context": "potvrzeni_o_soucasnem_pobytu_context"},
        "Žádost o uplatnění opatření proti nečinnosti": {
            "template": "zadost_o_uplatneni_opatreni_proti_necinnosti_spravniho_organu_Nin1.docx",
            "context": "necinnost_Nin1_context"
            },
        "Žádost o urychlení řízení": {
            "template": "zadost_urychleni_rizeni.docx",
            "context": "urychleni_rizeni_context"
            }
        }
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./views'),
    extensions=['jinja2.ext.i18n']
)


def docform(context):
    template = env.get_or_select_template('docform.tpl')
    system_context = {}
    context_to_pass = {}
    for key, value in context.items():
        if key.startswith('__'):
            system_context[key] = value
        else:
            # check if specific type of input is required, if no given it will be text
            elem = { 'value': value }
            radio = '__{}_radio'.format(key)
            date = '__{}_date'.format(key)

            if radio in context:
                elem['input'] = 'radio'
                elem['ids'] = context[radio]
            elif date in context:
                elem['input'] = 'date'
            else:
                elem['input'] = 'text'
            context_to_pass[key] = elem

    return template.render(context=context_to_pass,
                           name=context.get('__name__', "Application"),
                           system_context=system_context,
                           minvnitra_offices=get_offices_list())


@route('/')
def index():
    template = env.get_or_select_template('index.tpl')
    return template.render()


@route('/necinnost_Nin1')
def necinnost():
    context = _default_context('necinnost_Nin1_context')
    return docform(context)


@route('/rodne_cislo_application')
def rodne_cislo():
    context = _default_context('rodne_cislo_context')
    return docform(context)


@route('/historie_pobytu')
def historie_pobytu():
    context = _default_context('historie_pobytu_context')
    return docform(context)


@route('/potvrzeni_o_soucasnem_pobytu')
def potvrzeni_soucasny_pobyt():
    context = _default_context('potvrzeni_o_soucasnem_pobytu_context')
    return docform(context)


@route('/urychleni_rizeni')
def urychleni_rizeni():
    context = _default_context('urychleni_rizeni_context')
    return docform(context)


def get_office_by_name(name):
    return next((o for o in OFFICES if o['name'] == name), None)


@route('/get_office_address', method="POST")
def get_office_address():
    data = request.forms
    office = get_office_by_name(data.get('office'))
    return json.dumps(office or {})


@route('/generate', method="POST")
def generate():
    data = request.forms
    docx_template_name = TEMPLATE_MAP.get(data.get('__form__'), {}).get('template')
    default_context_name = TEMPLATE_MAP.get(data.get('__form__'), {}).get('context')
    if not docx_template_name or not default_context_name:
        return
    default_context = _default_context(default_context_name)
    # vet against default context keys
    user_input_vetted = {k: v for k, v in data.iteritems() if k in default_context and v}
    context = dict(default_context)
    context.update(user_input_vetted)
    # transition from YYYY-MM-DD dates to expected DD.MM.YYYY
    for date_key in [k for k in context if context.get('__{}_date'.format(k))]:
        try:
            context[date_key] = datetime.datetime.strptime(context[date_key], '%Y-%M-%d').strftime('%d.%M.%Y')
        except (TypeError, ValueError):
            # if anything breaks - just have it as is
            pass
    # process chosen office: substitute name with full information
    if '__chosen_office' in context:
        context['chosen_office'] = get_office_by_name(
                context.get('__chosen_office')) or get_office_by_name('Pracoviště Praha V.')
    # pass declination dicts if any present in context
    for key in [k for k in context if k.startswith('__declination')]:
        context[key.lstrip('__')] = context[key]
    with tempfile.NamedTemporaryFile(dir="generated", delete=True) as temp_doc:
        gen.generate_doc(docx_template_name, context, temp_doc.name)
        return static_file(
                temp_doc.name.rsplit(os.path.sep)[-1],
                root="generated/",
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                download=docx_template_name)

app = default_app()

if __name__ == '__main__':
    run(app, host='localhost', port=8080)
