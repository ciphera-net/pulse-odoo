{
    'name': "Pulse Analytics",
    # <series>.<major>.<minor>.<patch>, the scheme the Apps vendor guidelines
    # give as "major-minor-bugfix semantics (e.g. 10.0.1.1.3)". The series
    # prefix is Odoo 20.0, the current stable series — see RELEASING.md for
    # how that was confirmed and why this module does not target 19.0.
    'version': "20.0.1.0.0",
    'category': "Website",
    'summary': "Privacy-first web analytics. No cookies, no personal data, under 3 KB.",
    'description': """
Pulse Analytics
===============

Adds the Pulse Analytics tracking tag to every public page of this website.

Pulse Analytics (https://pulse.ciphera.net) is privacy-first web analytics by
Ciphera BV, a company in Belgium. Data is hosted in Switzerland. No cookies and
no personal data are stored, and the tracking script this module loads is
under 3 KB gzipped.

What this module does, completely: it adds one <script> tag, pointed at
https://js.ciphera.net/script.js, inside the <head> of every page the Website
app renders through "website.layout". The tracker auto-detects the domain
from the visitor's browser. There is no settings screen, because this module
is written entirely in XML — no Python files beyond the empty one Odoo
requires — so that it installs on Odoo Online, which refuses third-party
modules that contain custom Python. See the module's README for what that
trades away and how to work around it if you need to.

You need a Pulse Analytics account with a site registered for the same
domain. The free plan is enough to start: one site, 5,000 pageviews a month,
no card required.
""",
    'author': "Ciphera BV",
    'website': "https://pulse.ciphera.net",
    'support': "support@ciphera.net",
    # LGPL-3 per owner decision. Odoo Apps forces no licence (unlike Drupal,
    # Joomla and TYPO3, which require GPL and so cannot be Apache-2.0 like the
    # rest of the public Pulse integrations); Apache-2.0 is not itself one of
    # the manifest's six allowed values, and Odoo's own vendor guidelines
    # recommend LGPL-3 for open-source apps. See RELEASING.md and LICENSE.
    'license': "LGPL-3",
    # The ENTIRE dependency list. Depending on anything beyond the base
    # Website app would be a second thing to justify, and a wider surface for
    # a future change to accidentally need Python. tests/test_pulse_analytics.py
    # pins this list so it cannot grow unnoticed.
    'depends': ['website'],
    'data': [
        'views/pulse_tracker.xml',
    ],
    'installable': True,
    # A feature added to the Website app, not a standalone application in its
    # own right — it should not get a tile in the Odoo Apps launcher.
    'application': False,
    'auto_install': False,
}
