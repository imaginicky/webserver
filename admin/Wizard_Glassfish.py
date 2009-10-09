"""
Glassfish wizard.

Last update:
* Cherokee 0.99.25
* Glassfish
"""
import validations

from config import *
from util import *
from Page import *
from Wizard import *

NOTE_VSRV_NAME = _("Name of the new domain that will be created.")
NOTE_HOST_SRC = _('Hostname or IP of the server running Glassfish. You can add more later to have the load balanced.')
NOTE_HOST_PRT = _('Port running the service in said host. (Example: 8080)')
NOTE_WEB_DIR = _("Web folder under which Glassfish will be accessible.")

SOURCE = """
source!%(src_num)d!env_inherited = 0
source!%(src_num)d!type = host
source!%(src_num)d!nick = Glassfish %(src_num)d
source!%(src_num)d!host = %(src_host)s:%(src_port)d
"""

CONFIG_VSRV = SOURCE + """
%(vsrv_pre)s!nick = %(new_host)s
%(vsrv_pre)s!document_root = /dev/null

%(vsrv_pre)s!rule!1!match = default
%(vsrv_pre)s!rule!1!encoder!gzip = 1
%(vsrv_pre)s!rule!1!handler = proxy
%(vsrv_pre)s!rule!1!handler!balancer = round_robin
%(vsrv_pre)s!rule!1!handler!balancer!source!1 = %(src_num)d
%(vsrv_pre)s!rule!1!handler!in_allow_keepalive = 1
%(vsrv_pre)s!rule!1!handler!in_preserve_host = 0
"""

CONFIG_RULES = SOURCE + """
%(rule_pre)s!match = directory
%(rule_pre)s!match!directory = %(webdir)s
%(rule_pre)s!encoder!gzip = 1
%(rule_pre)s!handler = proxy
%(rule_pre)s!handler!balancer = round_robin
%(rule_pre)s!handler!balancer!source!1 = %(src_num)d
%(rule_pre)s!handler!in_allow_keepalive = 1
%(rule_pre)s!handler!in_preserve_host = 0
"""

DATA_VALIDATION = [
    ("tmp!wizard_glassfish!new_host",    (validations.is_new_host, 'cfg')),
    ("tmp!wizard_glassfish!new_webdir",   validations.is_dir_formated),
    ("tmp!wizard_glassfish!new_src_port", validations.is_tcp_port)
]

class Wizard_VServer_Glassfish (WizardPage):
    ICON = "glassfish.png"
    DESC = "New virtual server to proxy Glassfish projects."

    def __init__ (self, cfg, pre):
        WizardPage.__init__ (self, cfg, pre,
                             submit = '/vserver/wizard/Glassfish',
                             id     = "Glassfish_Page1",
                             title  = _("Glassfish Wizard"),
                             group  = WIZARD_GROUP_PLATFORM)

    def show (self):
        return True

    def _render_content (self, url_pre):
        txt = '<h1>%s</h1>' % (self.title)

        txt += '<h2>New Virtual Server</h2>'
        table = TableProps()
        self.AddPropEntry (table, _('New Host Name'), 'tmp!wizard_glassfish!new_host', NOTE_VSRV_NAME, value="glassfish.example.com")
        txt += self.Indent(table)

        txt += '<h2>Glassfish Project</h2>'
        table = TableProps()
        self.AddPropEntry (table, _('Source host'), 'tmp!wizard_glassfish!new_src_host', NOTE_HOST_SRC, value="localhost")
        self.AddPropEntry (table, _('Source port'), 'tmp!wizard_glassfish!new_src_port', NOTE_HOST_PRT, value=8080)
        txt += self.Indent(table)

        txt += '<h2>Logging</h2>'
        txt += self._common_add_logging()

        form = Form (url_pre, add_submit=True, auto=False)
        return form.Render(txt, DEFAULT_SUBMIT_VALUE)
        return txt

    def _op_apply (self, post):
        # Store tmp, validate and clean up tmp
        self._cfg_store_post (post)

        self._ValidateChanges (post, DATA_VALIDATION)
        if self.has_errors():
            return

        self._cfg_clean_values (post)

        # Incoming info
        new_host = post.pop('tmp!wizard_glassfish!new_host')
        src_host = post.pop('tmp!wizard_glassfish!new_src_host')
        src_port = int(post.pop('tmp!wizard_glassfish!new_src_port'))

        # Locals
        vsrv_pre = cfg_vsrv_get_next (self._cfg)
        src_num, src_pre = cfg_source_get_next (self._cfg)

        # Add the new rules
        config = CONFIG_VSRV % (locals())
        self._apply_cfg_chunk (config)
        self._common_apply_logging (post, vsrv_pre)


class Wizard_Rules_Glassfish (WizardPage):
    ICON = "glassfish.png"
    DESC = "New directory to proxy Glassfish projects."

    def __init__ (self, cfg, pre):
        WizardPage.__init__ (self, cfg, pre,
                             submit = '/vserver/%s/wizard/Glassfish'%(pre.split('!')[1]),
                             id     = "Glassfish_Page1",
                             title  = _("Glassfish Wizard"),
                             group  = WIZARD_GROUP_PLATFORM)

    def show (self):
        return True

    def _render_content (self, url_pre):
        txt = '<h1>%s</h1>' % (self.title)

        txt += '<h2>Glassfish Project</h2>'
        table = TableProps()
        self.AddPropEntry (table, _('Web Directory'), 'tmp!wizard_glassfish!new_webdir', NOTE_WEB_DIR, value="/glassfish")
        self.AddPropEntry (table, _('Source host'), 'tmp!wizard_glassfish!new_src_host', NOTE_HOST_SRC, value="localhost")
        self.AddPropEntry (table, _('Source port'), 'tmp!wizard_glassfish!new_src_port', NOTE_HOST_PRT, value=8080)
        txt += self.Indent(table)

        form = Form (url_pre, add_submit=True, auto=False)
        return form.Render(txt, DEFAULT_SUBMIT_VALUE)
        return txt

    def _op_apply (self, post):
        # Store tmp, validate and clean up tmp
        self._cfg_store_post (post)

        self._ValidateChanges (post, DATA_VALIDATION)
        if self.has_errors():
            return

        self._cfg_clean_values (post)

        # Incoming info
        webdir   = post.pop('tmp!wizard_glassfish!new_webdir')
        src_host = post.pop('tmp!wizard_glassfish!new_src_host')
        src_port = int(post.pop('tmp!wizard_glassfish!new_src_port'))

        # Locals
        rule_num, rule_pre = cfg_vsrv_rule_get_next (self._cfg, self._pre)
        src_num,  src_pre  = cfg_source_get_next (self._cfg)

        # Add the new rules
        config = CONFIG_RULES % (locals())
        self._apply_cfg_chunk (config)
