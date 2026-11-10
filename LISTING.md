# Odoo Apps listing — Pulse Analytics

The text and assets the Odoo Apps submission (`apps.odoo.com/apps/upload` →
"Register your Git repository", then the module's own description page once
the scan picks it up) will use. Not yet submitted — see RELEASING.md "Still
needed before publishing" and "What a human needs" for what is outstanding and
why it was not done here.

**Status:** 🟢 **LIVE since 09-11-2026** at
`https://apps.odoo.com/apps/modules/20.0/pulse_analytics`, from the repository registered as
`ssh://git@github.com/ciphera-net/pulse-odoo.git#20.0`. The store shows the description
page from `static/description/index.html` on the `20.0` branch, which must stay ASCII-only
(see RELEASING.md).

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

> Pulse Analytics counts visitors without cookies or stored IP addresses. The script this module adds is under 3 KB.

## Long description (for `static/description/index.html`)

Plain copy below; turning it into that file means wrapping it in the official
template's HTML (RELEASING.md), using only Bootstrap 4 utility classes for any
styling, no inline `<style>`, no `<script>`, and no links other than to assets
inside `static/description/` or to a canonical YouTube/Microsoft Teams URL —
all per the vendor guidelines' "Guidelines for the app's description page."

---

Pulse Analytics adds privacy-first web analytics to an Odoo website with one module. It sets no cookies and never stores IP addresses. The script it adds to your pages is under 3 KB.

**How it works**

1. Install the module. There is nothing to configure.
2. The module adds the tracking tag to every page your Website app serves. It reads the domain from each visitor's own browser, which is right for a site served on one domain.
3. Create a free account at pulse.ciphera.net, register your site, and your dashboard starts showing visitors as they arrive.

**What it measures**

Pulse counts pageviews, referrers, countries, devices, time on page and scroll depth, plus the goals, funnels and campaigns you set up, in one dashboard hosted in Europe. It does not count visitors whose browser sends Do Not Track or Global Privacy Control. The module never tags the Odoo backend and only touches the public website.

**You need**

Odoo 20.0 or 19.0 with the Website app, and a Pulse Analytics account with a site registered for the same domain. The free plan covers one site and 10,000 events a month, and you do not need a card. Every plan has every feature. Business starts at €9 a month with VAT.

**What this module does not do, by design**

This module has no settings screen. It is written entirely in XML, with no Python beyond the one empty file every Odoo module requires. If you need to pin a specific domain, add the interaction-events script, or route events through a custom API origin, paste the full tag into Odoo's own **Website → Configuration → Settings → SEO → Custom Code → Header** field instead. This module's README explains how and why.

Pulse Analytics is built by Ciphera, a company in Belgium. Data is hosted in Switzerland.

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

🟢 **Icon, description page and cover image built** (see below). The cover was added on 09-11-2026, the day
the store scored the module 4/5 for lacking one: see "Cover image" below.

- **`static/description/icon.png`**: ✅ done. 128×128 PNG, RGB with no alpha
  channel: the Pulse mark alone (never paired with Odoo's own mark) in white
  layers on the brand orange `#FD5E0F`, the same mark as Ciphera's profile
  pictures. The file is copied unchanged from Ciphera's brand set, revision v12
  (`https://cdn.ciphera.net/brand/v12/kit/odoo/pulse/icon.png`), and is not
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

### Cover image

`static/description/cover.png`, declared in the manifest's `images` key: 2400 x 1200 (2:1), the Pulse dashboard
from the docs' `dashboard-overview` capture (the public demo dashboard), its top left corner set over an orange
strip on a dark ground. That is the device of the changelog posts and the dashboard's What's new card, scaled to a
2:1 frame, with no added text. It shows the product, which is what the FAQ asks a cover to do (*"a full demo page
and not your company logo larger"*); the module itself has no screen of its own.

History: until 09-11-2026 this module shipped without a cover on purpose (the closest OCA analytics modules have
none, and a cover of the module itself could only have been the logo, larger). On its first day live the store
scored it 4/5 for exactly that, and the cover was added. Covers on the store measured that day (1200 x 600,
880 x 440, 1920 x 1080, 1152 x 648, 900 x 506, 540 x 303) are 2:1 or 16:9; the store serves them re-encoded as GIF.

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
real `icon.png`, an HTML `index.html` and, since 09-11-2026, a cover image: four of
the five. Rating depends on reviews.

## Trademark

Odoo is a trademark of Odoo S.A. The listing should not claim Odoo's
endorsement or affiliation — matching the independent-module line already in
README.md. No specific Odoo-brand disclaimer wording was found to be mandated
the way the Joomla Extensions Directory mandates one verbatim; this is a
general good-practice line, not a quoted requirement.
