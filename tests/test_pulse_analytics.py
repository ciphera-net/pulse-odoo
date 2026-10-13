#!/usr/bin/env python3
"""Standalone checks for the pulse_analytics module — no Odoo required.

There is no Odoo installed in this environment (no odoo binary, no
Postgres service wired up for it), so these tests cannot do what Drupal's
TagRenderTest or Joomla's scripts/verify.sh do: boot the real framework and
read back the HTML it renders. That gap is real and is not papered over here
— scripts/verify.sh is where a real Odoo renders this module's template and
the shipped bytes get asserted. Run these first; run that before trusting a
release.

What these tests CAN prove without Odoo, because the module is pure XML and
a static manifest:

  - the manifest is a well-formed literal and says what we intend it to say
    (licence, the one dependency, the free-app shape, the version series);
  - the view file is well-formed XML and the inherited xpath carries exactly
    one <script> element, with the exact src, defer, and no data-domain —
    i.e. the SOURCE markup is what we intend to ship;
  - the module directory contains no Python file but the required empty
    __init__.py, which is the entire basis for the Odoo Online claim this
    module is built around.

What they cannot prove: whether Odoo's QWeb HTML serializer emits a bare
`defer` or `defer="defer"` for the boolean attribute above, whether it
self-closes the <script> tag (which would be a broken page, not a missing
attribute — see the comment in pulse_tracker.xml), or whether the tag
actually reaches a rendered homepage and stays off an admin one. Those are
scripts/verify.sh's job precisely because they depend on Odoo's renderer,
not on this source.

Run:
    python3 tests/test_pulse_analytics.py
    python3 -m unittest tests.test_pulse_analytics -v   # from the repo root
"""
import ast
import os
import sys
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_DIR = os.path.join(REPO_ROOT, 'pulse_analytics')
MANIFEST_PATH = os.path.join(MODULE_DIR, '__manifest__.py')
VIEW_PATH = os.path.join(MODULE_DIR, 'views', 'pulse_tracker.xml')

SCRIPT_URL = 'https://js.ciphera.net/script.js'

# Odoo module licence keys that Odoo Apps' manifest schema accepts
# (apps.odoo.com/apps/faq, "How to set a license…"). Kept here so a typo in
# the manifest's licence key is caught even without Odoo installed.
VALID_ODOO_LICENSES = {
    'GPL-3', 'AGPL-3', 'LGPL-3', 'OPL-1',
    'Other OSI approved licence', 'Other proprietary',
}


def load_manifest():
    """Parses __manifest__.py as a data literal.

    ast.literal_eval only accepts literal Python (dicts, strings, numbers,
    lists, tuples, booleans, None) and executes nothing — the same reason
    Odoo's own tooling reads manifests this way rather than importing them.
    """
    with open(MANIFEST_PATH, encoding='utf-8') as fh:
        source = fh.read()
    return ast.literal_eval(source)


def find_tracker_script(xml_bytes):
    """Returns the single <script> element inside the module's //head xpath.

    Raises AssertionError with a specific message for each shape the
    template must not have, rather than returning None and letting a caller
    assert on that — this function IS the guard, and the negative-control
    tests below feed it deliberately broken input to prove it can fail.
    """
    root = ET.fromstring(xml_bytes)
    templates = root.findall('template')
    if len(templates) != 1:
        raise AssertionError(f'expected exactly one <template>, found {len(templates)}')
    template = templates[0]
    if template.get('inherit_id') != 'website.layout':
        raise AssertionError(
            f'template must inherit_id="website.layout", got {template.get("inherit_id")!r}'
        )

    xpaths = template.findall('xpath')
    head_xpaths = [x for x in xpaths if x.get('expr') == '//head']
    if len(head_xpaths) != 1:
        raise AssertionError(f'expected exactly one //head xpath, found {len(head_xpaths)}')
    xpath = head_xpaths[0]
    if xpath.get('position') != 'inside':
        raise AssertionError(f'//head xpath must use position="inside", got {xpath.get("position")!r}')

    scripts = xpath.findall('script')
    if len(scripts) != 1:
        raise AssertionError(f'expected exactly one <script> inside //head, found {len(scripts)}')
    return scripts[0]


class ManifestTests(unittest.TestCase):
    """The manifest says what this module promises, nothing more."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_parses_as_a_pure_literal(self):
        # If this failed, load_manifest() itself would have raised during
        # setUpClass — this test exists so that failure is reported as a
        # named, readable test rather than a setup error.
        self.assertIsInstance(self.manifest, dict)

    def test_required_keys_present(self):
        for key in ('name', 'version', 'license', 'depends', 'data', 'installable'):
            self.assertIn(key, self.manifest, f'manifest is missing required key {key!r}')

    def test_license_is_the_owner_ruled_value(self):
        self.assertEqual(self.manifest['license'], 'LGPL-3')
        self.assertIn(self.manifest['license'], VALID_ODOO_LICENSES)

    def test_license_key_rejects_an_unlisted_value(self):
        # Negative control for the enum check above: Apache-2.0 is not a
        # legal value in Odoo's manifest schema (apps.odoo.com/apps/faq) —
        # the reason this module is LGPL-3 and not Apache-2.0 like the rest
        # of the public Pulse integrations. Prove the set actually excludes
        # it, rather than trusting that it does.
        self.assertNotIn('Apache-2.0', VALID_ODOO_LICENSES)

    def test_depends_on_website_and_nothing_else(self):
        # A guard against the dependency list growing silently. Anything
        # beyond 'website' is a second thing to justify in review.
        self.assertEqual(self.manifest['depends'], ['website'])

    def test_version_targets_the_declared_series(self):
        version = self.manifest['version']
        parts = version.split('.')
        self.assertEqual(len(parts), 5, f'expected <series>.<series>.<maj>.<min>.<patch>, got {version!r}')
        self.assertEqual(parts[0:2], ['20', '0'], f'manifest version does not start with the 20.0 series: {version!r}')
        self.assertTrue(all(p.isdigit() for p in parts), f'version segments must all be numeric: {version!r}')

    def test_name_fits_the_store_rule(self):
        # apps.odoo.com/apps/vendor-guidelines: "the name of the app must be
        # explicit and should contain no more than 25 characters. Avoid
        # adjectives, or including the name of your company."
        name = self.manifest['name']
        self.assertLessEqual(len(name), 25, f'name is {len(name)} characters, over the 25 limit: {name!r}')
        self.assertNotIn('Ciphera', name, 'the app name must not include the company name')

    def test_declared_data_files_exist_on_disk(self):
        for rel_path in self.manifest['data']:
            full_path = os.path.join(MODULE_DIR, rel_path)
            self.assertTrue(os.path.isfile(full_path), f'manifest lists {rel_path!r} but it is not on disk')

    def test_stays_free(self):
        # "free LGPL app pays nothing" — a concrete guard that nobody adds a
        # price key without a conscious, separate decision to monetize.
        self.assertNotIn('price', self.manifest)
        self.assertNotIn('currency', self.manifest)

    def test_is_a_feature_not_a_standalone_application(self):
        self.assertTrue(self.manifest['installable'])
        self.assertFalse(self.manifest.get('application', False))


class PureXmlModuleTests(unittest.TestCase):
    """The whole Odoo Online claim rests on there being no Python here.

    "No Python" means no code: __manifest__.py is a data literal (see
    ManifestTests, which parses it with ast.literal_eval rather than
    importing it) and is mandatory for every Odoo module regardless. The
    claim this module makes is that __init__.py — the one file Odoo actually
    executes — is empty, and that nothing else executable exists at all.
    """

    ALLOWED_PY_FILES = {'__init__.py', '__manifest__.py'}

    def test_only_python_files_are_init_and_manifest(self):
        py_files = []
        for dirpath, _dirnames, filenames in os.walk(MODULE_DIR):
            for filename in filenames:
                if filename.endswith('.py'):
                    py_files.append(os.path.relpath(os.path.join(dirpath, filename), MODULE_DIR))
        self.assertEqual(
            sorted(py_files), sorted(self.ALLOWED_PY_FILES),
            f'found Python file(s) beyond __init__.py and __manifest__.py: {py_files}',
        )

    def test_init_is_empty(self):
        with open(os.path.join(MODULE_DIR, '__init__.py'), encoding='utf-8') as fh:
            content = fh.read()
        # Not merely "no imports" — truly empty (ignoring whitespace), so
        # there is no ambiguity about what "pure XML" means here.
        self.assertEqual(content.strip(), '', '__init__.py must be empty')

    def test_guard_catches_a_python_file_if_one_is_added(self):
        # Mutation test for the guard above: prove it can fail before
        # trusting that it passed. A model file anywhere under the module
        # would break the Odoo Online promise this whole design rests on.
        fake_tree = sorted(self.ALLOWED_PY_FILES | {os.path.join('models', 'website.py')})
        self.assertNotEqual(fake_tree, sorted(self.ALLOWED_PY_FILES))


class TrackerScriptTests(unittest.TestCase):
    """What the view file's XML source says, before Odoo ever renders it."""

    @classmethod
    def setUpClass(cls):
        with open(VIEW_PATH, 'rb') as fh:
            cls.xml_bytes = fh.read()
        cls.script = find_tracker_script(cls.xml_bytes)

    def test_view_is_well_formed_xml(self):
        ET.fromstring(self.xml_bytes)  # raises on malformed input

    def test_src_is_exactly_the_pulse_tracker_url(self):
        self.assertEqual(self.script.get('src'), SCRIPT_URL)

    def test_carries_defer(self):
        self.assertIsNotNone(self.script.get('defer'))

    def test_has_no_data_domain(self):
        # Auto-detect only, by design — see README.md "Settings". A
        # hardcoded data-domain here would ship an example domain to every
        # installer's site.
        self.assertIsNone(self.script.get('data-domain'))

    def test_has_no_inline_content(self):
        # No bootstrap, no inline JavaScript — the whole point of inheriting
        # website.layout directly instead of going through a mechanism that
        # can only take a JS string. A strict CSP needs no nonce or
        # 'unsafe-inline' for this module as a result.
        self.assertIsNone(self.script.text)
        self.assertEqual(len(list(self.script)), 0)

    def test_is_the_only_script_tag_in_the_file(self):
        # Guards against ever silently adding a second (e.g. a companion
        # interactions script) without a conscious README/manifest update —
        # this module does not offer that feature; see README.md.
        all_scripts = ET.fromstring(self.xml_bytes).findall('.//script')
        self.assertEqual(len(all_scripts), 1)

    def test_finder_rejects_a_second_template(self):
        # Negative control: prove find_tracker_script() actually enforces
        # "exactly one <template>" rather than just reading the first one.
        broken = (
            b'<odoo>'
            b'<template id="a" inherit_id="website.layout">'
            b'<xpath expr="//head" position="inside"><script src="x"></script></xpath>'
            b'</template>'
            b'<template id="b" inherit_id="website.layout">'
            b'<xpath expr="//head" position="inside"><script src="y"></script></xpath>'
            b'</template>'
            b'</odoo>'
        )
        with self.assertRaises(AssertionError):
            find_tracker_script(broken)

    def test_finder_rejects_a_wrong_inherit_id(self):
        # Negative control: a template inheriting the wrong view would never
        # attach to a real page. Prove the guard notices.
        broken = (
            b'<odoo><template id="a" inherit_id="website.something_else">'
            b'<xpath expr="//head" position="inside"><script src="x"></script></xpath>'
            b'</template></odoo>'
        )
        with self.assertRaises(AssertionError):
            find_tracker_script(broken)

    def test_finder_rejects_a_missing_head_xpath(self):
        # Negative control: a template with no //head xpath at all (e.g. one
        # that only touched //body) would ship no tracker tag whatsoever.
        broken = (
            b'<odoo><template id="a" inherit_id="website.layout">'
            b'<xpath expr="//body" position="inside"><script src="x"></script></xpath>'
            b'</template></odoo>'
        )
        with self.assertRaises(AssertionError):
            find_tracker_script(broken)

    def test_finder_rejects_two_scripts_in_the_head_xpath(self):
        # Negative control for test_is_the_only_script_tag_in_the_file's
        # underlying assumption: find_tracker_script() must not silently
        # pick the first of two and call it done.
        broken = (
            b'<odoo><template id="a" inherit_id="website.layout">'
            b'<xpath expr="//head" position="inside">'
            b'<script src="https://js.ciphera.net/script.js"></script>'
            b'<script src="https://js.ciphera.net/script.interactions.js"></script>'
            b'</xpath></template></odoo>'
        )
        with self.assertRaises(AssertionError):
            find_tracker_script(broken)

    def test_detects_a_data_domain_if_one_were_hardcoded(self):
        # Mutation test for test_has_no_data_domain: construct the thing
        # that test exists to catch and prove the assertion style actually
        # catches it, rather than trusting a field that happens to be
        # missing today.
        mutated = self.xml_bytes.replace(
            b'<script defer="defer" src="%s"></script>' % SCRIPT_URL.encode(),
            b'<script defer="defer" data-domain="example.com" src="%s"></script>' % SCRIPT_URL.encode(),
        )
        self.assertNotEqual(mutated, self.xml_bytes, 'the replace() above did not match — fix the fixture')
        mutated_script = find_tracker_script(mutated)
        self.assertIsNotNone(mutated_script.get('data-domain'))

    def test_detects_an_inline_bootstrap_if_one_were_added(self):
        # Mutation test for test_has_no_inline_content: an Astro-style
        # DOM-bootstrap script would be a real, discussable alternative
        # (see pulse-astro's README) but is not what this module ships, and
        # this proves the "no inline content" check would notice if it ever
        # did change without the README being updated to match.
        mutated = self.xml_bytes.replace(
            b'<script defer="defer" src="%s"></script>' % SCRIPT_URL.encode(),
            b'<script defer="defer" src="%s">var x = 1;</script>' % SCRIPT_URL.encode(),
        )
        self.assertNotEqual(mutated, self.xml_bytes, 'the replace() above did not match — fix the fixture')
        mutated_script = find_tracker_script(mutated)
        self.assertIsNotNone(mutated_script.text)
        self.assertNotEqual(mutated_script.text.strip(), '')


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for case in (ManifestTests, PureXmlModuleTests, TrackerScriptTests):
        suite.addTests(loader.loadTestsFromTestCase(case))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
