# Pulse Analytics for Odoo

Privacy-first analytics for an Odoo website, in one module. No cookies, no
personal data, and the script it adds to your pages is under 3 KB.

[Pulse Analytics](https://pulse.ciphera.net) is built by
[Ciphera](https://ciphera.net), a company in Belgium, and hosted in Europe.

## Requirements

Odoo 20.0, the current stable series as of this writing — see RELEASING.md for
how that was confirmed, and why this module does not target 19.0 despite
earlier plans naming it. The Website app (installed by default on a new
database). No Composer/npm dependencies, no database tables, no Python at all
beyond the empty file every Odoo module requires. You need a Pulse Analytics
account with a site registered for the same domain; the free plan is enough to
start.

## Install

On Odoo Online, from the Apps screen, once this module is listed on Odoo Apps
(see RELEASING.md). On Odoo.sh or on-premise:

```bash
# copy pulse_analytics/ into your addons path, then
odoo -d your-database -i pulse_analytics
```

There is nothing to configure afterwards. The tracker reads the visitor's own
browser hostname, which is correct for a site served on one domain — the usual
case.

## Settings

There are none, and that is a decision, not an oversight. See "Why no
settings" below.

## Three things worth knowing

**What lands in your pages is the tag, built from exactly the same XML anchor
Odoo's own "Custom Code" feature uses** (`website.layout`, the same template
`custom_code_layout` inherits in Odoo's own source):

```html
<script defer src="https://js.ciphera.net/script.js"></script>
```

No `data-domain` — the tracker auto-detects the hostname — and no inline
JavaScript at all, so **a strict Content-Security-Policy needs no nonce and no
`unsafe-inline` for this module** — only `script-src https://js.ciphera.net`
and `connect-src https://pulse-api.ciphera.net`.

⚠️ Which exact bytes Odoo's QWeb renderer emits for the boolean `defer`
attribute — a bare `defer`, like Drupal, or `defer="defer"`, like TYPO3 — and
whether it writes the element as `<script …></script>` rather than something
self-closing, are facts about Odoo's HTML serializer, not about this module's
source, and this repository has no Odoo installed to render through. They are
exactly what `scripts/verify.sh` asserts against a real Odoo instance, and that
script's own comments record what it found once it has been run. Don't take
the snippet above as a byte-for-byte claim until that has happened — see
`tests/test_pulse_analytics.py`'s module docstring for the same point made
about the test suite.

**It never reaches the backend, and there is no toggle for that because there
is nothing to toggle.** `website.layout` is Odoo's public frontend layout.
Odoo's backend (`/odoo`, `/web`) is an entirely separate Owl/JS client that
never renders through it, so this module's tag cannot leak onto an admin
screen by construction — not by an early return that could be gotten wrong,
and not by a setting that defaults the right way but could be flipped. It does
render inside the website editor's live preview when someone edits a page,
which is real frontend content, not an admin screen, so that is correct too.

**It runs on every page the Website app serves**, including a page rendered on
behalf of eCommerce, the blog, the forum, or any other Odoo app that builds its
pages on `website.layout` — which is the entire addressable surface of "this
Odoo site's public pages," by construction, since that is the one layout the
Website app's page renderer uses.

## Why no settings

A Pulse install elsewhere (Drupal, Joomla, TYPO3, Astro…) lets you pin a
domain, add a companion script for clicks/copies/form submits, and route
through a custom API origin. None of those are possible here without writing a
Python model field to store the choice — and a module with any Python beyond
the required empty `__init__.py` **cannot be installed on Odoo Online**, which
refuses third-party modules containing custom Python
([apps.odoo.com/apps/faq](https://apps.odoo.com/apps/faq): *"Third-party apps
sold on Odoo Apps cannot be used on Odoo Online, unless they are data-modules
(that do not include any python files)"*). That is the trade this module
makes, deliberately, and it is worth being honest about rather than faking a
settings screen that silently does nothing or that only half-works.

Three things we looked at and did not do, and why:

- **A domain field.** `website.website` already carries a `domain` field
  (Website → Configuration → Settings → Website Domain, used for
  multi-website routing by hostname) that is tempting to read from a QWeb
  expression and reuse as Pulse's `data-domain`. We decided against it: that
  field means "the hostname Odoo uses to pick which website record answers an
  incoming request," which is a different thing from "the domain this site is
  registered under in Pulse," and the two coinciding is a coincidence a
  multi-website installer should not have to reason about. On a single-website
  install — the common case — the field is usually left empty anyway, which
  would just mean this module silently does nothing differently from today.
  If you need a specific domain pinned (a staging deployment, a site that
  answers on several hostnames), paste the full tag by hand into Odoo's own
  **Website → Configuration → Settings → SEO → Custom Code → Header** field
  instead of installing this module — that field already exists, needs no
  module, and takes the exact tag with whatever attributes you want on it.
- **The companion script** (clicks, copies and form submits — see the Drupal,
  Joomla and TYPO3 READMEs for the same feature). Same constraint: a toggle
  needs somewhere to persist the choice. If you want it, add a second
  `<script defer src="https://js.ciphera.net/script.interactions.js"></script>`
  line next to this module's own tag via the Custom Code field above, or fork
  this module for an on-premise/Odoo.sh install where you control the addons
  path and can add your own `res.config.settings` field.
- **A custom API origin.** Same reasoning again — pasted into Custom Code if
  you need it, which is also exactly how Odoo's own cookie-consent gate
  expects a hand-added third-party script to arrive (see below).

## It does not go through Odoo's cookie-consent gate, and that is intentional

Odoo's "Custom Code" head/footer fields are filtered by
`website._control_third_party_trackers_in_html()`: if the site's cookies bar
is enabled, `block_third_party_domains` is on, and a visitor has not granted
optional-cookie consent, any `<script>`/`<iframe>` in that text whose `src`
matches the site's blocked-domains list has its `src` rewritten to
`about:blank`. Pulse Analytics sets no cookies, so being gated behind cookie
consent would be the wrong behaviour for it specifically — and this module
avoids the question entirely by inheriting `website.layout` directly, the same
way Odoo's own `custom_code_layout` template does, rather than writing into
the `custom_code_head` field that mechanism actually filters. Confirmed
against Odoo 20.0's own source
(`addons/website/models/website.py`,
`_control_third_party_trackers_in_html`/`_should_remove_third_party_trackers`)
before this module was written — see RELEASING.md.

One practical consequence: if you ever add `js.ciphera.net` or `ciphera.net`
to this site's own **Blocked Third-Party Domains** list (Website →
Configuration → Settings, under "Block 3rd-party domains"), that list is only
consulted against the `custom_code_head`/`custom_code_footer` fields — it has
no effect on this module's tag either way, because this module was never
routed through that filter to begin with.

## What Pulse Analytics measures

Pageviews, referrers, countries, devices, time on page and scroll depth, plus
goals, funnels and campaigns. It sets no cookies and stores no personal data.
Visitors whose browser sends Do Not Track or Global Privacy Control are not
counted at all — so if you test in Brave or Firefox and see nothing, that is
the tracker behaving correctly. Safari is the easiest browser to verify an
install in.

## Licence

**LGPL-3**, by owner decision. Odoo Apps does not force a licence the way
drupal.org, the Joomla Extensions Directory and TYPO3's own licensing policy
force GPL-2.0-or-later/GPL on everything they host — see the Drupal, Joomla
and TYPO3 READMEs for that constraint. The manifest's `license` key is instead
a fixed enum (`GPL-3`, `AGPL-3`, `LGPL-3`, `OPL-1`, `Other OSI approved
licence`, `Other proprietary`) with **no Apache-2.0 value**, so Apache-2.0 —
what every other public Pulse integration uses — was never on the table as a
literal choice; it would have had to be declared as the vaguer `Other OSI
approved licence`. Odoo's own vendor guidelines recommend `LGPL-3` "for open
source apps," which is the value used here. `LICENSE` at the repository root
is the LGPL-3.0 text verbatim from
[gnu.org/licenses/lgpl-3.0.txt](https://www.gnu.org/licenses/lgpl-3.0.txt).

Odoo is a trademark of Odoo S.A. This is an independent module and is not
affiliated with or endorsed by Odoo S.A. or the Odoo project.
