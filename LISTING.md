# Odoo Apps listing — Pulse Analytics

The text and assets the Odoo Apps submission (`apps.odoo.com/apps/upload` →
"Register your Git repository", then the module's own description page once
the scan picks it up) will use. Not yet submitted — see RELEASING.md "Still
needed before publishing" and "What a human needs" for what is outstanding and
why it was not done here.

**Status:** 🔴 **NOT SUBMITTED.** The task that produced this module forbids any
remote, push or publish action; this file is the copy ready for whoever runs
that step, matching the pattern of `pulse-joomla/LISTING.md`.

## Where the fields come from

Most of this listing is **not a web form** the way Joomla's JED or Google's GTM
gallery are. From `apps.odoo.com/apps/faq` ("How to set up an icon, cover image
and description for your modules?"): *"The rich-text HTML description comes
from the `static/description/index.html` file in the module folder."* So the
long description below is copy to turn into that file (template-derived, per
RELEASING.md), not text typed into a dashboard. `name`, `summary`, `license`,
`support`, `website`, `category` come straight from `__manifest__.py` — see
that file, not a separate form, for the values actually shipping.

## Name

**Pulse Analytics** (15 characters — the manifest's own 25-character ceiling,
confirmed in `tests/test_pulse_analytics.py`).

## Short description (the `summary` manifest key)

> Privacy-first web analytics. No cookies, no personal data, under 3 KB.

## Long description (for `static/description/index.html`)

Plain copy below; turning it into that file means wrapping it in the official
template's HTML (RELEASING.md), using only Bootstrap 4 utility classes for any
styling, no inline `<style>`, no `<script>`, and no links other than to assets
inside `static/description/` or to a canonical YouTube/Microsoft Teams URL —
all per the vendor guidelines' "Guidelines for the app's description page."

---

Pulse Analytics adds privacy-first web analytics to an Odoo website with one
module. It sets no cookies, stores no personal data, and the script it adds to
your pages is under 3 KB.

**How it works**

1. Install the module. There is nothing to configure.
2. The tracking tag is added to every page your Website app serves,
   automatically. It reads the domain from each visitor's own browser, which
   is correct for a site served on one domain.
3. Create a free account at pulse.ciphera.net, register your site, and your
   dashboard starts showing visitors as they arrive.

**What it measures**

Pageviews, referrers, countries, devices, time on page and scroll depth, plus
the goals, funnels and campaigns you set up — in one dashboard, hosted in
Europe. Visitors whose browser sends Do Not Track or Global Privacy Control are
not counted at all. The Odoo backend is never tagged; this module only ever
touches the public website.

**You need**

Odoo 20.0 with the Website app, and a Pulse Analytics account with a site
registered for the same domain. The free plan is enough to start: one site,
5,000 pageviews a month, no card required. Every feature is available on every
plan; paid plans begin at €11/month for more volume.

**What this module does not do, by design**

This module has no settings screen — it is written entirely in XML, with no
Python beyond the one empty file every Odoo module requires, so that it also
installs on Odoo Online, which does not allow third-party modules that contain
custom Python. If you need to pin a specific domain, add the interaction-events
script, or route through a custom API origin, paste the full tag into Odoo's
own **Website → Configuration → Settings → SEO → Custom Code → Header** field
instead — see this module's README for exactly how and why.

Pulse Analytics is built by Ciphera, a company in Belgium. Data is hosted in
Switzerland.

Documentation: <https://docs.ciphera.net/pulse>

---

## Fields from `__manifest__.py`

- **Category:** `Website` (the manifest's `category` key — Odoo Apps groups
  listings by this field; `Website` is the closest fit to what the module does
  and the convention other analytics add-ons for the Website app use. Not
  independently confirmed against a live category picker, since registering a
  repository needs a signed-in apps.odoo.com account — see RELEASING.md.)
- **Licence:** LGPL-3 (see README.md "Licence" and `LICENSE`)
- **Support email:** support@ciphera.net
- **Author / website:** Ciphera BV / <https://pulse.ciphera.net>
- **Tags:** no dedicated tag field was found on the registration form itself
  (it is sign-in gated — see RELEASING.md); `category` is the only
  machine-readable grouping this module's manifest controls.

## Links

Website `https://pulse.ciphera.net` · Documentation
`https://docs.ciphera.net/pulse` · Support `support@ciphera.net` · Source
`https://github.com/ciphera-net/pulse-odoo`

## Screenshots and images needed before publishing

None exist in this repository yet — see RELEASING.md "Still needed before
publishing." What the store actually uses, per the FAQ:

- **`static/description/icon.png`** — a real PNG (not a renamed file of
  another format), square. Shows as a white cube until this exists.
- **A cover image / thumbnail**, referenced from the manifest's `images` key
  (e.g. `'images': ['static/description/images/cover_screenshot.png']`) — the
  FAQ: *"the first picture with a name ending with '_screenshot' will be
  selected and displayed as big screenshot... to show a full demo page and not
  your company logo larger."* So this should be a real screenshot of a Pulse
  dashboard (or the rendered tag in a page's `<head>` via dev tools), not the
  Pulse logo blown up.
- Both need to come from the same Pulse-mark asset pipeline the other
  platform listings use (`pulse-framer/listing/`), not be drawn fresh for this
  one listing.

## Scoring

The vendor guidelines publish five ranking criteria directly: no icon, no cover
image, no licence set in the manifest, a rating below 3, and a non-HTML
description (e.g. plain `.rst`) each cost points, independent of anything about
the module's functionality. This module already has `license` set in the
manifest; the icon, cover image and an HTML `static/description/index.html`
are the three open items against that list (see above).

## Trademark

Odoo is a trademark of Odoo S.A. The listing should not claim Odoo's
endorsement or affiliation — matching the independent-module line already in
README.md. No specific Odoo-brand disclaimer wording was found to be mandated
the way the Joomla Extensions Directory mandates one verbatim; this is a
general good-practice line, not a quoted requirement.
