import collections
import datetime
import jinja2
import json
import os
import tempfile
import yaml

from bottle import default_app, request, route, run, static_file

import exc
import generate as gen


# These are the fields that are not related to a specific form
SYSTEM_CONTEXT = ["name", "postal_address", "datova_schranka", "link", "authority", "declination"]


def get_form_context(filename):
    """Returns a default context dict"""
    data = {}
    with open(filename, encoding='utf-8') as f:
        if filename.endswith('.yaml'):
            # context is a yaml file
            context = yaml.safe_load(f)
            document = context.get('document', {})
            try:
                # transform system keys to __key__
                document = context['document']
                for key in [k for k in SYSTEM_CONTEXT if k in document]:
                    data['__{}__'.format(key)] = document[key]
                    # flatten dict in case of declinations - pass a dict of declinationPAD
                    if key == "declination":
                        for pad, values in document["declination"].items():
                            declination_key = "__declination{}".format(pad)
                            data[declination_key] = {v["before"]: v["after"] for v in values}
                # process form fields
                form_fields = document['form'].get('fields', [])
                sorted_data = collections.OrderedDict()
                for field in form_fields:
                    data[field["name"]] = field.get("default", "")
                    if field.get("type", "text") != "text":
                        # XXX FIXME this will be refactored in the near future
                        # need to pass control type to the frontend:
                        # - date is specified by the presence of __name__date: True
                        # - radio has the format __name__radio: choices
                        specific_format = "__{}_{}".format(field["name"], field["type"])
                        if field["type"] == "date":
                            data[specific_format] = True
                        else:
                            data[specific_format] = field.get("choices", [])
            except KeyError as err:
                raise exc.ConfigError("{} raised when processing {}".format(err, filename))
        else:
            # context is a json file
            try:
                data = json.loads(f.read())
            except:
                raise exc.ConfigError("Error parsing json config {}".format(filename))
        # specific context dict post-processing
        if data['__postal_address__'] == 'minvnitra_offices_chooser':
            data['__chosen_office'] = None
        return data


def get_offices_list():
    with open('minvnitra_offices', encoding='utf8') as f:
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
    context = get_form_context('necinnost_Nin1_context.yaml')
    return docform(context)


@route('/rodne_cislo_application')
def rodne_cislo():
    context = get_form_context('rodne_cislo_context.yaml')
    return docform(context)


@route('/historie_pobytu')
def historie_pobytu():
    context = get_form_context('historie_pobytu_context.yaml')
    return docform(context)


@route('/potvrzeni_o_soucasnem_pobytu')
def potvrzeni_soucasny_pobyt():
    context = get_form_context('potvrzeni_o_soucasnem_pobytu_context.yaml')
    return docform(context)


@route('/urychleni_rizeni')
def urychleni_rizeni():
    context = get_form_context('urychleni_rizeni_context.yaml')
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
    default_context = get_form_context(default_context_name)
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
