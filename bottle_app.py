import jinja2
import json
import os
import tempfile

from bottle import default_app, request, route, run, static_file

import generate as gen


def _default_context(filename):
    """Returns a default context dict"""
    with open(filename) as f:
        try:
            return json.loads(f.read())
        except:
            return {}

DEFAULT_CONTEXT_FILE = 'necinnost_trvaly_context'
DEFAULT_CONTEXT_DICT = _default_context(DEFAULT_CONTEXT_FILE)
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
            elem = {'value': value}
            spec_input_key = '__{}_radio'.format(key)
            if spec_input_key in context:
                elem['input'] = 'radio'
                elem['ids'] = context[spec_input_key]
            else:
                elem['input'] = 'text'
            context_to_pass[key] = elem

    return template.render(context=context_to_pass,
                           name=context.get('__name__', "Application"),
                           system_context=system_context)


@route('/')
def index():
    template = env.get_or_select_template('index.tpl')
    return template.render()


@route('/necinnost_trvaly_pobyt')
def necinnost_trvaly_pobyt():
    context = _default_context('necinnost_trvaly_context')
    return docform(context)


@route('/generate', method="POST")
def generate(docx_template_name="zadost_o_uplatneni_opatreni_proti_necinnosti_spravniho_organu.docx", context=None):

    data = request.forms
    # vet against default context keys
    user_input_vetted = {k: v for k, v in data.iteritems() if k in DEFAULT_CONTEXT_DICT and v}
    context = dict(DEFAULT_CONTEXT_DICT)
    context.update(user_input_vetted)
    with tempfile.NamedTemporaryFile(dir="generated", delete=True) as temp_doc:
        gen.generate_doc(docx_template_name, context, temp_doc.name)
        return static_file(
                temp_doc.name.rsplit(os.path.sep)[-1],
                root="generated/",
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                download=docx_template_name)

app = default_app()
