# Pulse Analytics for Odoo

This module adds privacy-first analytics to an Odoo website. Pulse Analytics
sets no cookies and never stores IP addresses, and the script it adds to your
pages is under 3 KB.

[Pulse Analytics](https://pulse.ciphera.net) is built by
[Ciphera](https://ciphera.net), a company in Belgium, and hosted in Europe.

## Requirements

This module needs Odoo 20.0 or 19.0, and the Website app, which Odoo installs
together with this module if the database does not have it yet. The `20.0`
branch holds the 20.0 build and the `19.0` branch the 19.0 build; they differ
only in the version series in the manifest. The module has no Composer or
npm dependencies and adds no database tables. The only Python in it is the
empty file every Odoo module requires. You need a Pulse Analytics account with
a site registered for the same domain; the free plan is enough to start.

## Install

Odoo Online runs the 19 series, so an Odoo Online database can only install the
19.0 build, once Odoo Apps lists it. Installing on Odoo Online has not been
tested yet. On Odoo.sh or on-premise, use these steps:

```bash
# copy pulse_analytics/ into your addons path, then
odoo -d your-database -i pulse_analytics
```

There is nothing to configure afterwards. The tracker reads the visitor's own
browser hostname, which is correct for a site served on one domain (the usual
case).

## Settings

The module has no settings, and that is deliberate. See "Why no settings"
below.

## Three things worth knowing

**What lands in your pages is the tag, built from the same XML anchor that
Odoo's own "Custom Code" feature uses** (`website.layout`, the same template
`custom_code_layout` inherits in Odoo's own source):

```html
<script defer="defer" src="https://js.ciphera.net/script.js"></script>
```

The tag has no `data-domain` attribute, because the tracker auto-detects the
hostname. The module adds no inline JavaScript, so a strict
Content-Security-Policy does not need a nonce or `unsafe-inline` for this
module. It needs only `script-src https://js.ciphera.net` and
`connect-src https://pulse-api.ciphera.net`.

QWeb's HTML serializer writes the boolean `defer` attribute as `defer="defer"`,
which matches the source XML's own spelling byte for byte. It does not collapse
the attribute to a bare `defer`, as Drupal's renderer does. The element is a
real open/close pair, `<script …></script>`, and is never self-closed. These
are facts about Odoo's serializer. They could not be verified until an Odoo
instance rendered the page, and they have now been confirmed against real
Odoo 20.0 and Odoo 19.0 instances (`scripts/verify.sh`, run in Docker, with
`ODOO_IMAGE=odoo:19.0` for 19).

**The tag never reaches the authenticated backend, and there is no toggle for
that because there is nothing to toggle. It does reach the public login page,
and that is correct.** `website.layout` is Odoo's public frontend layout. The
authenticated backend (the Owl/JS SPA at `/odoo`, and `/web` once logged in)
is a client-rendered app that never server-renders through `website.layout`,
so this module's tag cannot reach it. This was confirmed by logging in and
reading that page. `/web/login` itself is different. When the `website` module
is installed (this module depends on it, so it always is), Odoo's own
`website` controller overrides `/web/login` to render through `website.layout`
for a themed, on-brand login page. That is the same anchor this module's tag
is attached to, and the same one Odoo's own Custom Code field would reach too.
So the tag appears on the pre-login form (a page anyone, logged in or not, can
load). It does not appear on anything behind it. It also renders inside the
website editor's live preview when someone edits a page. The preview shows real
frontend content, so the tag is correct there too.

**It runs on every page the Website app serves.** That includes a page rendered
on behalf of eCommerce, the blog, the forum, or any other Odoo app that builds
its pages on `website.layout`, which is the one layout the Website app's page
renderer uses. Together these cover all of this Odoo site's public pages.

## Why no settings

A Pulse install elsewhere (Drupal, Joomla, TYPO3, Astro and others) lets you
pin a domain, add a companion script for clicks, copies and form submits, and
route through a custom API origin. None of those are possible here without
writing a Python model field to store the choice. A module with any Python
beyond the required empty `__init__.py` cannot be installed on Odoo Online,
which refuses third-party modules containing custom Python
([apps.odoo.com/apps/faq](https://apps.odoo.com/apps/faq): *"Third-party apps
sold on Odoo Apps cannot be used on Odoo Online, unless they are data-modules
(that do not include any python files)"*). That is the trade this module makes,
deliberately. A settings screen here would silently do nothing or only half
work, so the module does not fake one.

We looked at three things and did not do them, for these reasons:

- **A domain field.** `website.website` already carries a `domain` field
  (Website → Configuration → Settings → Website Domain, used for
  multi-website routing by hostname) that is tempting to read from a QWeb
  expression and reuse as Pulse's `data-domain`. We decided against it: that
  field means "the hostname Odoo uses to pick which website record answers an
  incoming request", which is a different thing from "the domain this site is
  registered under in Pulse", and a multi-website installer should not have to
  reason about whether the two happen to coincide. On a single-website install
  (the common case) the field is usually left empty anyway, so reading it
  would silently change nothing from what the module does today. If you need a
  specific domain pinned (a staging deployment, a site that answers on several
  hostnames), skip this module and paste the full tag by hand into Odoo's own
  **Website → Configuration → Settings → SEO → Custom Code → Header** field.
  That field already exists, needs no module, and takes the exact tag with
  whatever attributes you want on it.
- **The companion script.** It covers clicks, copies and form submits, and the
  Drupal, Joomla and TYPO3 READMEs describe the same feature. The same
  constraint applies: a toggle needs somewhere to persist the choice. If you
  want it, add a second
  `<script defer src="https://js.ciphera.net/script.interactions.js"></script>`
  line next to this module's own tag via the Custom Code field above, or fork
  this module for an on-premise or Odoo.sh install where you control the
  addons path and can add your own `res.config.settings` field.
- **A custom API origin.** The same reasoning applies here. If you need one,
  paste it into Custom Code, which is also how Odoo's own cookie-consent gate
  expects a hand-added third-party script to arrive (see below).

## It does not go through Odoo's cookie-consent gate, and that is intentional

Odoo's "Custom Code" head/footer fields are filtered by
`website._control_third_party_trackers_in_html()`: if the site's cookies bar
is enabled, `block_third_party_domains` is on, and a visitor has not granted
optional-cookie consent, any `<script>`/`<iframe>` in that text whose `src`
matches the site's blocked-domains list has its `src` rewritten to
`about:blank`. Pulse Analytics sets no cookies, so gating it behind cookie
consent would be the wrong behaviour for it. This module avoids the question:
it inherits `website.layout` directly, the same way Odoo's own
`custom_code_layout` template does, and it does not write into the
`custom_code_head` field that this mechanism filters. This was confirmed
against Odoo 20.0's own source (`addons/website/models/website.py`,
`_control_third_party_trackers_in_html`/`_should_remove_third_party_trackers`)
before this module was written (see RELEASING.md).

One practical consequence: if you add `js.ciphera.net` or `ciphera.net` to this
site's own **Blocked Third-Party Domains** list (Website → Configuration →
Settings, under "Block 3rd-party domains"), that list is consulted only against
the `custom_code_head`/`custom_code_footer` fields. It has no effect on this
module's tag either way, because the module was never routed through that
filter.

## What Pulse Analytics measures

Pulse Analytics measures pageviews, referrers, countries, devices, time on page and scroll depth, plus goals, funnels and campaigns.
It sets no cookies and never stores IP addresses.
Visitors whose browser sends Do Not Track or Global Privacy Control are not counted, so if you test in Brave or Firefox and see nothing, the tracker is behaving correctly.
Safari is the easiest browser to verify an install in.

## Licence

This module is licensed under LGPL-3, by owner decision. Odoo Apps does not
force a licence the way drupal.org, the Joomla Extensions Directory and TYPO3's
own licensing policy force GPL-2.0-or-later/GPL on everything they host (see
the Drupal, Joomla and TYPO3 READMEs for that constraint). The manifest's
`license` key is a fixed enum (`GPL-3`, `AGPL-3`, `LGPL-3`, `OPL-1`,
`Other OSI approved licence`, `Other proprietary`) with no Apache-2.0 value.
Apache-2.0, which most other public Pulse integrations use, was therefore
never on the table as a literal choice. It would have had to be declared as the
vaguer `Other OSI approved licence`. Odoo's own vendor guidelines recommend
`LGPL-3` "for open source apps", which is the value used here. `LICENSE` at the
repository root is the LGPL-3.0 text verbatim from
[gnu.org/licenses/lgpl-3.0.txt](https://www.gnu.org/licenses/lgpl-3.0.txt).

Odoo is a trademark of Odoo S.A. This is an independent module and is not
affiliated with or endorsed by Odoo S.A. or the Odoo project.
