# Releasing pulse_analytics (Odoo)

## 🔴 Targets Odoo 20.0, not 19.0 — the brief named 19.0 and that is now stale

The task that produced this module said "current series 19.0 (verify)" and
asked for the app-store registration example in the fragment-tagged form the
strategy doc (`Pulse/docs/plans/14-09-2026-integration-marketplaces-strategy.md`,
§11a/§6a) recorded on 15-09-2026: `ssh://git@github.com/ciphera-net/pulse-odoo#19.0`.
That doc is a month old. Measured directly against Odoo's own sources today:

| Source | What it says |
|---|---|
| `odoo.com/documentation/*/administration/standard_extended_support.html` (shared support table) | **Odoo 20.0 — release date September 2026**, full ● support on Odoo Online, Odoo.sh and on-premise. Odoo 19.0 — September 2025, still supported but no longer current. |
| `odoo.com/page/download` | Lists **Odoo 20** before Odoo 19 before Odoo 18 — current-first ordering. |
| `github.com/odoo/odoo` branches | `20.0` exists and is a real, populated branch (`addons/website/...` present and current). |

So Odoo 20.0 shipped in September 2026, a month before this module was built,
and is the current stable series. This module, its manifest version
(`20.0.1.0.0`), and the registration commands below all target **20.0**. The
mechanism the strategy doc recorded — ssh URI with the series in the fragment,
the `online-odoo` GitHub user, one module folder per repo root, "any error will
unpublish all the modules from your repository" — is unchanged and is carried
below verbatim from the doc and from Odoo's own FAQ/vendor-guidelines pages
(re-fetched directly, not re-quoted from the doc, so these are current as of
this writing). Only the **series number** in the registration example is
corrected from `#19.0` to `#20.0`. The lesson is general, not specific to this
module: a month is enough for an annual-release platform's "current" series to
move, so re-measure a dated plan against the live platform before building
from it rather than trusting the date on the doc.

If a later session needs 19.0 specifically (an existing customer still on it,
for instance), the module itself needs no logic change — only the manifest
`version` prefix and a second git branch; the view file and tests are
version-agnostic. `_control_third_party_trackers_in_html`, the `domain` field's
behaviour, and `custom_code_layout`'s shape were all re-checked against 20.0's
source directly (both `models/website.py` and `views/website_templates.xml`)
and are structurally identical to 19.0's — nothing here was invalidated by the
version correction, only the target series number.

## Odoo does not pre-review, and there is no CI pipeline here

Verbatim from `apps.odoo.com/apps/faq` ("Are there any specific rules that
Apps authors must observe?"):

> *"We do not currently review every module published, but we do take action
> when users report abusive behavior."*

There is no CI registered for this repository, the same reasoning as
pulse-drupal: Odoo Apps' only gate is a repository **scan** at registration
and on every push (it raises an error on a non-existent dependency or a
malformed manifest, per the vendor guidelines below), not a test run. `python3
tests/test_pulse_analytics.py` is this repository's local equivalent, and
`scripts/verify.sh` is the real-install check nothing else here runs for you.

## Registering the repository — verbatim facts, from the strategy doc and re-confirmed live

From `apps.odoo.com/apps/faq` ("Can I use Odoo Apps modules with Odoo Online
(SaaS)?"):

> *"Third-party apps sold on Odoo Apps cannot be used on Odoo Online, unless
> they are data-modules (that do not include any python files)."*

This is the entire reason this module has no Python beyond the empty
`__init__.py` every Odoo module needs — see README.md "Why no settings" and
`tests/test_pulse_analytics.py`'s `PureXmlModuleTests`.

**Repository URL format** — from the FAQ ("How do I format the URL of my
repository?"), verbatim:

> *"All repositories URL's will follow the standard ssh URI scheme... the url
> will look like `ssh://git@gitServer(:port)/mypath#version`... for example for
> GitHub, it should be something like `ssh://git@github.com/odoo/odoo#9.0`."*

For this repository, registered as:

```
ssh://git@github.com/ciphera-net/pulse-odoo#20.0
```

**Repository access** — from the same FAQ entry, verbatim:

> *"If you are on Github, you can simply authorize our **online-odoo** user
> (NOT odoo-online) on your repository (the authorization must be done on the
> repository specifically, not the entire company)."*

So: GitHub repo Settings → Collaborators → invite `online-odoo` (not
`odoo-online` — the FAQ calls this out explicitly because it is an easy typo)
**on `ciphera-net/pulse-odoo` itself**, not an org-wide grant. The repository
can be public — the FAQ separately says *"Public repositories should only host
free modules to protect proprietary code and licenses"* and this module is
free, so that is not a reason to keep it private.

**One module folder per repository root** — from the vendor guidelines
(`apps.odoo.com/apps/vendor-guidelines`), the rule the task brief already
names, confirmed live:

> *"Each module needs to be in a separate folder at the root of the
> repository, even if there is only one module."*

This repository has exactly one: `pulse_analytics/` at the root.

**Branch name equals series** — the task brief marks this UNVERIFIED in the
strategy doc and nothing found while building this module resolved it either;
the FAQ's only branch-naming evidence is the `#9.0` example above, which is
consistent with but does not prove a hard requirement. Push this repository's
release branch as **`20.0`**, matching the fragment used to register it and
every first-party Odoo repository's own convention, and treat the question as
still open rather than assume it one way.

**A bad manifest takes the whole repository down** — vendor guidelines,
verbatim:

> *"A good manifest is essential as any error will unpublish all the modules
> from your repository."*

This repository has exactly one module, so the blast radius is one module —
but the mechanism (a scan-time manifest error unpublishing more than the
module you just touched, if there were others) is exactly as the task brief
describes it, and is why `tests/test_pulse_analytics.py`'s `ManifestTests`
parse the manifest the same cautious way (`ast.literal_eval`, never `import`)
and check every field the vendor guidelines call "Mandatory."

## Manifest requirements, verbatim from the vendor guidelines

Mandatory fields and their rules, each checked by `ManifestTests`:

- **`name`**: *"must be explicit and should contain no more than 25
  characters. Avoid adjectives, or including the name of your company."*
  `"Pulse Analytics"` is 15 characters and names neither an adjective nor
  Ciphera.
- **`version`**: *"should include the Odoo version and follow major-minor-
  bugfix semantics (e.g. 10.0.1.1.3)."* `20.0.1.0.0` here.
- **`license`**: enum `GPL-3` / `AGPL-3` / `LGPL-3` / `OPL-1` / `Other OSI
  approved licence` / `Other proprietary` — see README.md "Licence" for why
  this is `LGPL-3` and not Apache-2.0.
- **`depends`**: *"the list must contain all the dependencies needed to run
  the module. A non-existing dependency will raise an error during the scan of
  the repository."* `['website']`, the entire list.

Optional fields used here: `summary`, `support` (*"the email address to be
used for claims or support requests"* — `support@ciphera.net`, matching the
other Pulse integration listings). Not used: `price`/`currency` (the module is
free — *"If the price is not set, the application is free"*), `live_test_url`
(would need a real, maintained demo Odoo instance; not set up for this
module), `images` (see "Still needed before publishing" below).

**The licence file**, from the same FAQ entry:

> *"The license file is loaded from the LICENSE file at the root of your
> module or, if there is none, at the root of your repository."*

`LICENSE` is at the repository root (this repo has exactly one module, so
either location satisfies this). Unlike drupal.org's packaging — which adds a
`LICENSE.txt` for you and asks contributors not to commit one — Odoo expects
the author to provide it, so this repository commits the LGPL-3.0 text
verbatim from gnu.org, matching the file list `git ls-files` shows.

## Still needed before publishing — real, not fabricated

🟢 **The icon and description page were built 14-10-2026** and are on `main`
and `20.0` (reviewed before the push: icon spans closed explicitly, the sign-up
address named in plain text).
What that work found and did, each measured against real accepted modules
rather than guessed — see `LISTING.md` "Screenshots and images needed before
publishing" for the full detail and the "Why no cover image" / "Why no
hyperlinks" sections for the two things deliberately left out:

- **`pulse_analytics/static/description/icon.png`**: done. From the FAQ:
  *"the module icon needs to be located at `static/description/icon.png`...
  Please note that changing the file extension of an image does not change
  its format"* (it must be a real PNG, not a renamed one). Satisfied: a real
  128×128 RGB PNG with no alpha channel, the Pulse mark on the dark ground
  `#0a0a0a`, copied unchanged from Ciphera's brand set, revision v6
  (`https://cdn.ciphera.net/brand/v6/kit/odoo/pulse/icon.png`). It is not
  drawn or resized here. The FAQ names no size, so 128×128 was read directly
  off three real, accepted free Odoo modules (`OCA/website`'s
  `website_analytics_matomo`, `website_cookiebot`, `website_require_login`, all
  128×128 with a transparent corner; core Odoo modules measure 100×100 and one
  OCA module 70×70, so "square and transparent" is the invariant, not one
  exact pixel count). This icon keeps the size and the square but not the
  transparency: it sits on a solid dark tile by design. The file built on
  14-10-2026 was the transparent RGBA version, and this one replaced it on
  19-10-2026.
- **`pulse_analytics/static/description/index.html`** — done. The FAQ:
  *"The rich-text HTML description comes from the static/description/index.html
  file ... It is recommended to start with this official template"*, linking
  `github.com/odoo/odoo/blob/11.0/addons/crm/static/description/index.html` —
  that exact template's class vocabulary (`oe_container`, `oe_slogan`,
  `oe_span6`/`oe_span12`, `oe_dark`, `oe_mt*`/`oe_mb*`) is what this file
  uses, cross-checked against `odoo/odoo`'s own `website`, `project`,
  `mass_mailing` and `point_of_sale` description pages at the same 11.0 tag.
  No `<script>`, no `<style>` block, only `style="color:…"` on headings (one
  of the attributes the vendor guidelines name as permitted alongside
  Bootstrap 4 classes) — the copy drafted in `LISTING.md` was restructured
  into this shape, not typed fresh.
- **A cover image** (`images` manifest key) — deliberately **not** added.
  Optional (it only affects the Apps Store ranking score, see `LISTING.md`
  "Scoring"), and the two closest real comparables on `OCA/website`
  (`website_analytics_matomo`, `website_cookiebot`) ship without one; the one
  OCA module that does declare one (`website_google_tag_manager`) points at a
  file that 404s in the published repository. This module has no UI of its
  own to screenshot, so a cover here would be exactly what the FAQ says not
  to do — *"a full demo page and not your company logo larger"* — the logo,
  larger. See `LISTING.md` "Why no cover image" for the measurement.
- Odoo's "Register your Git repository" form itself is sign-in gated (seen
  directly: `apps.odoo.com/apps/upload` shows *"Please sign in to be able to
  register a repository"* to an anonymous request), so the actual registration
  step needs an authenticated apps.odoo.com account — not run as part of this
  task, or the one that added the icon and description page.

## What a human needs, and for which step

| Step | Needs | Who/what |
|---|---|---|
| ✅ Push the repo to GitHub as `ciphera-net/pulse-odoo`, branch `20.0` (done 14-10-2026) | a GitHub account with create-repo rights on `ciphera-net` | the project's canonical git identity |
| ✅ Authorise Odoo's access (invite sent 14-10-2026, read-only) | GitHub repo Settings → Collaborators, invite `online-odoo` on this repo specifically | GitHub repo admin |
| Register the repository | an apps.odoo.com account, signed in, `apps/upload` → "Register your Git repository" with the `ssh://git@github.com/ciphera-net/pulse-odoo#20.0` URL | an Odoo.com account (create one if none exists; this is a separate credential from GitHub) |
| ✅ Icon and `index.html` on `main`/`20.0` (14-10-2026) | a reviewer, then a push | repo admin |
| Watch for a scan error | re-reading the module page after registering, or after any push | same apps.odoo.com account |

What is left is the registration itself: an apps.odoo.com account, then
`apps/upload` → "Register your Git repository" with the `20.0` URL above.

## No CI — but `scripts/verify.sh` has now been run for real

This repository still has no CI configured (same reasoning as pulse-drupal:
Odoo Apps' only gate is a registration-time manifest scan, not a test run).
`scripts/verify.sh` has since been run for real, in Docker, against
`odoo:20.0` — see its own header comment and README.md's "Three things worth
knowing" for what it found: the exact serialized bytes of the `defer`
attribute, and the website-rendered-login-page vs. authenticated-backend
distinction. Two defects in the script itself (an HTTP bind-interface default
Odoo 20.0 changed, and a negative control that was silently installing the
module it was meant to prove absent) were found and fixed in the course of
that run; see git log for the commits.

🟢 **`scripts/verify.sh` was re-run on 19-10-2026 with the icon and
`index.html` in place.** The 14-10-2026 listing-assets work did not re-run it,
because that task ran under a hard Docker prohibition. It ran
`python3 tests/test_pulse_analytics.py` instead (25/25), which does not touch
`static/description/` at all. Neither file changes what Odoo renders in a
page's `<head>`, and the re-run agrees: against `odoo:20.0` (Odoo
20.0-20261015) with `postgres:16` it ended with `ALL CHECKS PASSED`. The script
does not check the icon, so that result shows the module still installs and
serves the same tag. It says nothing about how the icon renders in the store.
