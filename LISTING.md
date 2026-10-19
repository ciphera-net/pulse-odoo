# Odoo Apps listing — Pulse Analytics

The text and assets the Odoo Apps submission (`apps.odoo.com/apps/upload` →
"Register your Git repository", then the module's own description page once
the scan picks it up) will use. Not yet submitted — see RELEASING.md "Still
needed before publishing" and "What a human needs" for what is outstanding and
why it was not done here.

**Status:** 🔴 **NOT SUBMITTED.** The task that produced this module forbids any
remote, push or publish action; this file is the copy ready for whoever runs
that step, matching the pattern of `pulse-joomla/LISTING.md`.

🟢 **`static/description/icon.png` and `static/description/index.html` now
exist** (on `main` and `20.0` since 14-10-2026) — see "Screenshots
and images needed before publishing" below for what was built and why, and
RELEASING.md for how the icon size and the index.html structure were measured
against real accepted modules rather than guessed.

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

🟢 **Icon and description page built** (see below); the cover image was
deliberately **not** added — see "Why no cover image" below.

- **`static/description/icon.png`**: ✅ done. 128×128 PNG, RGB with no alpha
  channel: the Pulse mark alone (never paired with Odoo's own mark) on the
  dark ground `#0a0a0a`. The file is copied unchanged from Ciphera's brand
  set, revision v6
  (`https://cdn.ciphera.net/brand/v6/kit/odoo/pulse/icon.png`), and is not
  resized or re-encoded here. The size was not guessed:
  `static/description/icon.png` was read directly off three real, accepted
  free modules on the Odoo Apps store (measured 14-10-2026).
  `OCA/website`'s `website_analytics_matomo` (the closest comparable, an
  analytics module) and `website_cookiebot` are both **128×128 with a
  transparent corner**; `website_require_login` matches; Odoo's own core
  `website`/`website_sale`/`website_blog` modules use 100×100 and OCA's
  `website_google_tag_manager` uses 70×70. All of them are square and
  transparent, none on a solid tile. This icon matches them on size and shape
  but sits on a solid dark tile by design, so it has no transparent corner.
- **`static/description/index.html`** — ✅ done. Built from the exact template
  `apps.odoo.com/apps/faq` names as official
  (`github.com/odoo/odoo/blob/11.0/addons/crm/static/description/index.html`):
  `oe_container`/`oe_row oe_spaced`/`oe_slogan`/`oe_span6`/`oe_span12`/
  `oe_dark`/`oe_mt*`/`oe_mb*` classes, no `<script>`, no `<style>` block, no
  external links other than a plain-text mention of `docs.ciphera.net/pulse`
  (not a hyperlink — see "Why no hyperlinks" below). Cross-checked against
  real modules' own `index.html` (`odoo/odoo`'s `website`, `project`,
  `mass_mailing`, `point_of_sale` at the 11.0 tag the FAQ itself links) for
  the class vocabulary, including an all-text two-column section with no
  screenshot at all (`website`'s own "SEO Tools" / "Call to Action" pair),
  which is the shape this module's page follows throughout since there is no
  dashboard screenshot to show.

### Why no cover image

The manifest's `images` key was **not** added. Measured against the three
closest real precedents on `OCA/website` (14-10-2026): the directly-comparable
analytics module, `website_analytics_matomo`, has no `images` key at all;
neither does `website_cookiebot`. `website_google_tag_manager` does declare
one (`static/description/website_google_tag_manager.png`) — but that exact
file **404s** in the published repository, i.e. even an accepted, listed
module ships a dead reference for this field, which is further evidence it is
optional and not load-bearing. The FAQ's own description of the field — *"to
show a full demo page and not your company logo larger"* — describes exactly
the trap a Pulse cover would fall into: this module has no UI of its own to
screenshot, so any image here would be the Pulse mark blown up, the one thing
the guidance says not to do. The icon already carries the mark; a cover adding
nothing but a bigger copy of it is skipped. (This updates the "should be a
real screenshot of a Pulse dashboard... not the Pulse logo blown up" line that
used to be here — RELEASING.md "Still needed before publishing" still listed
it as outstanding before this measurement.)

### Why no hyperlinks in index.html

The vendor guidelines restrict `index.html` links to resources inside
`static/description`, canonical YouTube/Microsoft Teams URLs, and `mailto:`/
`skype:` — not a generic marketing or docs URL. Confirmed by absence: across
the five real `index.html` files read for this (the official template plus
`website`/`project`/`mass_mailing`/`point_of_sale`), the only non-local `href`
found anywhere is one YouTube link; nothing links to the vendor's own site.
So `docs.ciphera.net/pulse` is written as plain text in the description page,
not wrapped in `<a href>` — the manifest's own `website`/`support` keys (see
`__manifest__.py`) are what the Apps store itself turns into the listing's
"Author Website" and support links, outside this file.

## Scoring

The vendor guidelines publish five ranking criteria directly: no icon, no cover
image, no licence set in the manifest, a rating below 3, and a non-HTML
description (e.g. plain `.rst`) each cost points, independent of anything about
the module's functionality. This module has `license` set in the manifest, a
real `icon.png`, and an HTML `index.html` — three of the five addressed. "No
cover image" is the one still true here, deliberately — see "Why no cover
image" above for why a Pulse cover would cost more than the ranking point it
buys (it would be the logo blown up, which the FAQ names as the thing to
avoid). Rating is outside this task's control until the module has reviews.

## Trademark

Odoo is a trademark of Odoo S.A. The listing should not claim Odoo's
endorsement or affiliation — matching the independent-module line already in
README.md. No specific Odoo-brand disclaimer wording was found to be mandated
the way the Joomla Extensions Directory mandates one verbatim; this is a
general good-practice line, not a quoted requirement.
